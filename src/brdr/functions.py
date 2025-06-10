import logging
import subprocess
import requests
import re
from rdflib import Graph
from rdflib.namespace import RDF
import os
import json

LOG = logging.getLogger(__name__)


class ConfigServer:
    def __init__(self, url: str, user: str, password: str):
        self.__url = url
        self.__user = user
        self.__password = password
        self.__HEADERS = {"Content-type": "application/json", "Accept": "application/json" }

    def get(self, path):
        url = f"{self.__url}/{path}.json"
        req = requests.get(url,
                           auth=(self.__user, self.__password),
                           headers=self.__HEADERS)
        if req.status_code != 200:
            raise requests.HTTPError(
                f"Get failed with status_code {req.status_code} and message '{req.text}'.")
        return req.json()


class SSOID:
    def __init__(self, openam_endpoint: str, user: str, password: str) -> object:
        self.__url = openam_endpoint
        self.__user = user
        self.__password = password
        self.set_token()

    def set_token(self):
        payload = {
            "username": self.__user,
            "password": self.__password
        }
        res = requests.post(self.__url, data=payload)
        if res.status_code != 200:
            raise requests.HTTPError(
                f"Get failed with status_code {res.status_code} and message '{res.text}'.")
        else:
            self.TOKEN = res.text.replace("token.id=", "").rstrip('\n')



class RDF:
    def __init__(self, context: object, json: object, dspace_download: str):
        self.__construct(dspace_download, Graph().parse(data={'@graph': json, '@context': context}, format='json-ld'))
    def __construct(self, dspace_download, g):
        query = f"""
            PREFIX dc:      <http://purl.org/dc/elements/1.1/>
            PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
            PREFIX dcat:    <http://www.w3.org/ns/dcat#>
            CONSTRUCT {{
                ?distributie a dcat:Distribution.
                ?d dcat:downloadURL ?downloadurl .
                }}
            WHERE {{
                ?stuk dossier:isVoorgesteldDoor ?distributie.
                ?s dossier:isVoorgesteldDoor ?d ;
                dc:identifier ?identifier .
                bind(iri(concat('{dspace_download}', ?identifier)) as ?downloadurl)
                }} """
        query2 = f"""
            PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
            PREFIX dbo:	<http://dbpedia.org/ontology/> 
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            CONSTRUCT {{
                ?dossier dossier:isNeerslagVan ?zaak .
                ?zaak a dbo:Case ;
                rdfs:label ?label .
                }}
            WHERE {{
                ?dossier a dossier:Dossier ;
                rdfs:label ?label .
                bind(iri(REPLACE(STR(?dossier), "https://data.omgeving.vlaanderen.be/id/entity/", "https://data.omgeving.vlaanderen.be/id/case/", "i") ) as ?zaak)
                }} """
        query3 = f"""
            PREFIX prov:    <http://www.w3.org/ns/prov#>
            CONSTRUCT {{
                ?o a prov:Collection .
                }}
            WHERE {{
                ?s ?p ?o.
                FILTER CONTAINS(str(?o),"/id/collection/")  
                }} """
        query4 = "SELECT distinct ?s ?p ?o  WHERE { ?s ?p ?o }"
        self.__graph = g.query(query).graph + g.query(query2).graph + g.query(query3).graph + g
        self.turtle = self.__graph.serialize(format='n3', indent=4)
        x = 0
        for row in self.__graph.query(query4):
            x = x + 1
        LOG.info(f"Collection metadata transformed to {str(x)} triples.")
        #LOG.info(f"Turtle file:\n {self.turtle}")

class Dspace:
    def __init__(self, instance: str, token: str):
        self.__instance = instance
        self.set_headers(token)

    def get_items_in_collection(self, number: int, collection: str):
        URL = f"http://{self.__instance}:8080/rest/api/collections/{number}/items?expand=all"
        dspace_response = requests.get(URL, headers=self.__headers)
        if dspace_response.status_code != 200:
            raise requests.HTTPError(
                f"Get failed with status_code {dspace_response.status_code} and message '{dspace_response.text}'.")
        self.__merge_metadata_and_bitstreams(dspace_response.json(), collection)

    def set_headers(self, token: str):
        LOG.info(f"Setting headers for extraction on {self.__instance}")
        self.__headers = {'OpenAMSSOID': token, 'Accept': 'application/json'}

    def is_connected(self):
        """Status of the connection, test if ssoid is still valid."""
        url_status = f"http://{self.__instance}:8080/rest/api/status"
        dspace_response = requests.get(url_status, headers=self.__headers)
        LOG.info(f"Authentication to {self.__instance} {dspace_response.reason}. Connected: {dspace_response.ok}!")
        return dspace_response.ok

    def __merge_metadata_and_bitstreams(self, items: object, collection: str):
        self.metadata = None
        result = []
        for item in items:
            """Metadata list of objects to metadata dictionary."""
            metadata_dictionary = self.__flatten_metadata(item.get('metadata', []))
            metadata_dictionary['collection'] = 'col:' + collection
            """Add bitstream object(s) to metadata dictionary !!! only one bitstream alowed"""
            if len(item.get('bitstreams', [])) > 0 :
                bitstreams = []
                for bitstream in item.get('bitstreams', []):
                    bitstream['collection'] = 'col:' + collection
                    bitstreams.append(bitstream)
                metadata_dictionary['bitstream'] = bitstreams
                if len(item.get('bitstreams', [])) > 1 :
                    LOG.warning(f"""Dspace item {metadata_dictionary['vlaanderen.identifier']} has {str(len(item.get('bitstreams', [])))} bitstreams.""")
            """Append metadata dictionary to result array"""
            result.append(metadata_dictionary)
        """Clean json: int/float->str ; xs:date->xs:dateTime ; adjust domains, classnames, ..."""
        self.metadata = self.__dossier_prefix(self.__fix_iso_dates(self.__convert_numbers_to_strings(result)))

    def __flatten_metadata(self, metadata_list: object):
        """Turn metadata list into a single dictionary."""
        return {item['key']: item['value'] for item in metadata_list}

    def __convert_numbers_to_strings(self, obj: object):
        """Recursively convert numbers to strings."""
        if isinstance(obj, dict):
            return {k: self.__convert_numbers_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.__convert_numbers_to_strings(v) for v in obj]
        elif isinstance(obj, (int, float)):
            return str(obj)
        else:
            return obj

    def __fix_iso_dates(self, obj: object):
        """Append T00:00:00 to yyyy-mm-dd dates without time component."""
        if isinstance(obj, dict):
            return {k: self.__fix_iso_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.__fix_iso_dates(v) for v in obj]
        elif isinstance(obj, str):
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', obj):
                return obj + "T00:00:00"
            return obj
        else:
            return obj

    def __dossier_prefix(self, obj: object):
        """change @base to dossier: prefix in dc.type ; adjust concepts cfr. oslo:Dossier + omv_dossier:Dossier"""
        if isinstance(obj, dict):
            obj["dc.type"] = "dossier:" + obj["dc.type"]
            if re.fullmatch(r'dossier:Procedurestap', obj["dc.type"]):
                obj["dc.type"] = "omv_dossier:ProcedurestapNeerslag"
            if re.fullmatch(r'dossier:Document', obj["dc.type"]):
                obj["dc.type"] = "dossier:Stuk"
            return obj
        elif isinstance(obj, list):
            return [self.__dossier_prefix(v) for v in obj]
        else:
            return obj

class Virtuoso:
    def __init__(self, host: str,
                 graph_uri: str,
                 username: str,
                 password: str):
        self.__tempfile = '/tmp/rdf.ttl'
        self.__host = host
        self.__graph_uri = graph_uri
        self.__username = username
        self.__password = password
        self.__url = f"http://{self.__host}:8080/sparql-graph-crud-auth?graph-uri={self.__graph_uri}"

    def upload_rdf_to_graph(self, rdf: str, content_type: str = "text/turtle") :
        with open(self.__tempfile, "w") as f:
            f.write(rdf)
        cmd = f"""curl --url "{self.__url}" -X POST --digest -u {self.__username}:{self.__password} -s -H 'Content-Type: {content_type}'  -T {self.__tempfile} -w "%{{http_code}}" """
        #cmd = f"""curl --url "{self.__url}" -X POST --digest -u {self.__username}:{self.__password} -s -H 'Content-Type: {content_type}' -w "%{{http_code}}" --data-urlencode '{rdf}' """
        s = subprocess.check_output(cmd, shell=True)
        if int(s.decode("utf-8")) <= 201:
            LOG.info(f"Loaded RDF to Graph {self.__graph_uri} on {self.__host}")
        else:
            LOG.error(f"""Loading RDF to Graph {self.__graph_uri} on {self.__host} returned {s.decode("utf-8")}""")
        self.__delete_temp_file()

    def delete_graph(self) :
        cmd = f"""curl --digest -u {self.__username}:{self.__password} -s --url "{self.__url}" -X DELETE -w "%{{http_code}}" """
        s = subprocess.check_output(cmd, shell=True)
        if int(s.decode("utf-8")) == 200:
            LOG.info(f"Graph {self.__graph_uri} on {self.__host} deleted")
        else:
            LOG.error(f"""Deletion of Graph {self.__graph_uri} on {self.__host} returned {s.decode("utf-8")} """)

    def __delete_temp_file(self):
        if os.path.exists(self.__tempfile):
            os.remove(self.__tempfile)