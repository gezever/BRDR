jq '. + {wkt: ("POLYGON((" + (.geometry.shape | fromjson |  .coordinates[0] |  map("\(.0) \(.1)") |   join(", ")) +   "))") }'


jq '.geometry += {wkt: ("POLYGON((" + (.geometry.shape | fromjson | .coordinates[0] |  map("\(.0) \(.1)") |   join(", ") ) + "))")

jq '.geometry += { wkt: ("POLYGON((" + (.geometry.shape | fromjson |  .coordinates[0] |  map("\(.[0]) \(.[1])") |  join(", ") ) + "))")}'

jq '.geometry += {  shape_wkt: ( "POLYGON((" + (.geometry.shape | fromjson |   .coordinates[0] | map("\(.[0]) \(.[1])") | join(", ")) + "))" ), boundingBox_wkt: ( "POLYGON((" + (.geometry.boundingBox | fromjson | .coordinates[0] |map("\(.[0]) \(.[1])") |join(", ")) + "))"), center_wkt: ( "POINT(" +(.geometry.center | fromjson |.coordinates | "\(.[0]) \(.[1])") + ")")}' input.json

curl -H 'Accept: application/json' https://geo.api.vlaanderen.be/capakey/v2/parcel/24504D0693/00B000?geometry=full | jq '{"@context": {"geo": "http://www.opengis.net/ont/geosparql#","sf": "http://www.opengis.net/ont/sf#", "locn": "http://www.w3.org/ns/locn#", "capakey": "https://data.vlaanderen.be/id/perceel/", "adres": {  "@id": "locn:address", "@container": "@set" }, "geometry": { "@id": "geo:hasGeometry"}, "wkt": {"@id": "geo:asWKT", "@type": "geo:wktLiteral" }, "type": "@type" }, "@id": ("https://data.vlaanderen.be/id/perceel/" + .capakey),  "capakey": .capakey, "municipalityName": .municipalityName,  "departmentName": .departmentName,   "sectionCode": .sectionCode,  "grondnummer": .grondnummer, "exponent": .exponent, "bisnummer": .bisnummer,  "adres": .adres, "geometry": { "type": "sf:Polygon", "wkt": ( "POLYGON((" + ((.geometry.shape | fromjson | .coordinates[0] |  map("\(.[0]) \(.[1])") | join(", ") ) ) + "))") }}'


Bij een request als http://localhost/id/perceel/24504D0693/00B000 met accept header text/turtle doet de webapplicatie onderliggend een request met curl analoog curl -H 'Accept: application/json' https://geo.api.vlaanderen.be/capakey/v2/parcel/24504D0693/00B000?geometry=full
