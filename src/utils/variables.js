'use strict';

import fs from "fs";
import jsonld from "jsonld";


const context = JSON.parse(fs.readFileSync('source/context.json', 'utf8'));
const frame_grondboring2 = {
    "@context": context,
    "@type": ["grondboringen:Grondboring"],
    "qualifiedAssociation": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "wasStartedBy": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "boorder": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "boormeester": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "actuations": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "opdrachtgever": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "samplings": {
        "@embed": "@never",
        "@omitDefault": true
    },


}

const frame_observation = {
    "@context": context,
    "@type": ["sosa:Observation"],
    "used": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "observedProperty": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "hasResult": {
        "@embed": "@always",
        "@omitDefault": true
    },
    "hasFeatureOfInterest": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "madeBySensor": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "usedProcedure": {
        "@embed": "@never",
        "@omitDefault": true,
    },

}
const frame_association = {
    "@context": context,
    "@type": ["prov:Association"],

    "hadPlan": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "hadRole": {
        "@embed": "@never",
        "@omitDefault": true
    }

}


const frame_agent = {
    "@context": context,
    "@type": ["prov:Agent"],
    actedOnBehalfOf: {
        "@embed": "@never",
        "@omitDefault": true
    }
}


const frame_actuation = {
    "@context": context,
    "@type": ["sosa:Actuation"],
    "generated": {
        "@embed": "@always",
        "@omitDefault": true,
        "hadMember": {
            "@embed": "@never",
            "@omitDefault": true
        },
    },
    "hasResult": {
        "@embed": "@always",
        "@omitDefault": true,
        "hadMember": {
            "@embed": "@never",
            "@omitDefault": true
        },
    },
    "used":  {
        "@embed": "@never",
        "@omitDefault": true,
    },
    "hasFeatureOfInterest": {
        "@embed": "@never",
        "@omitDefault": true,
    },
    "actsOnProperty": {
        "@embed": "@never",
        "@omitDefault": true,
    },

    "madeByActuator": {
        "@embed": "@never",
        "@omitDefault": true
    },
    "usedProcedure": {
        "@embed": "@never",
        "@omitDefault": true,
    },
}


const frame_geometry = {
    "@context": context,
    "@type": ["geosparql:Geometry"]
}

const frame_observableProperty = {
    "@context": context,
    "@type": ["sosa:ObservableProperty"],
    "isActedOnBy":{
        "@embed": "@never",
        "@omitDefault": true
    },
    "isPropertyOf":{
        "@embed": "@never",
        "@omitDefault": true
    }

}



const frame_procedure = {
    "@context": context,
    "@type": ["sosa:Procedure"],
}

const frame_list = {
    "@context": context,
    "@type": ["rdf:List"],
    "first":{
        "@embed": "@never",
        "@omitDefault": true
    },
    "rest":{
        "@embed": "@never",
        "@omitDefault": true
    },
}



const sortLines = str => Array.from(new Set(str.split(/\r?\n/))).sort().join('\n'); // To sort the dump of the reasoner for turtle pretty printing. Easier than using the Sink or Store.

async function rdf_to_jsonld(nt, frame) {
    let rdf = await sortLines(nt);
    console.log("rdf to jsonld");
    let my_json = await jsonld.fromRDF(rdf);
    console.log("Extract ... as a tree using a frame.");
    return await jsonld.frame(my_json, frame);
}

const prefixes = {
    "adms": "http://www.w3.org/ns/adms#",
    "dcterms": "http://purl.org/dc/terms/",
    "geosparql": "http://www.opengis.net/ont/geosparql#",
    "gml": "http://www.opengis.net/ont/gml#",
    "prov": "http://www.w3.org/ns/prov#",
    "qudt-schema": "https://qudt.org/schema/qudt/",
    "qudt-unit": "https://qudt.org/vocab/unit/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "sdmx-attribute": "http://purl.org/linked-data/sdmx/2009/attribute#",
    "seb": "https://data.vlaanderen.be/ns/sensoren-en-bemonstering#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sosa": "http://www.w3.org/ns/sosa/",
    "sosa-om": "http://www.w3.org/ns/sosa/om#",
    "ssn": "http://www.w3.org/ns/ssn/",
    "time": "http://www.w3.org/2006/time#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
}

export {
    prefixes,
    frame_observation,
    frame_actuation,
    frame_association,
    frame_agent,
    frame_procedure,
    frame_list,
    frame_observableProperty,
    frame_geometry,
    rdf_to_jsonld,
    sortLines
};