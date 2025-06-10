import logging
from dspacerdf.functions import Dspace, RDF, SSOID, Virtuoso, ConfigServer
import json
import os
import dotenv

LOG = logging.getLogger(__name__)

dotenv.load_dotenv()
config = ConfigServer(url=os.environ.get("configserver_url").rstrip("/"),
                      user=os.environ.get("configserver_user"),
                      password=os.environ.get("configserver_password")).get('nifitransformatie-dspacerdf')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/context.json')) as ct:
    context = json.load(ct)

sso = SSOID(openam_endpoint=config['openam']['endpoint'],
            user=config['openam']['systeem_gebruiker'],
            password=config['openam']['systeem_gebruiker_password'])

virtuoso = Virtuoso(host=config['virtuoso']['instance'],
                    graph_uri=config['virtuoso']['graph'],
                    username=config['virtuoso']['virtuoso_rw_username'],
                    password=config['virtuoso']['virtuoso_rw_password'])
virtuoso.delete_graph()

dspace = Dspace(instance=config['dspace']['instance'],
                token=sso.TOKEN)

def fetch_transform_load(collectie):
    if dspace.is_connected():
        dspace.get_items_in_collection(number=config['dspace']['collectie'][collectie], collection=collectie)
        rdf = RDF(context=context,
                  json=dspace.metadata,
                  dspace_download=config['dspace']['source'][collectie]['download'])
        virtuoso.upload_rdf_to_graph(rdf=rdf.turtle,
                                     content_type="text/turtle")
    else:
        sso.set_token()
        dspace.set_headers(sso.TOKEN)
        fetch_transform_load(collectie)

for collectie in config['dspace']['source']:
    LOG.info(f"Start fetch_transform_load collectie: {collectie}.")
    fetch_transform_load(collectie)
