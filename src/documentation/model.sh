#!/bin/bash  

#declare -a files=("alignment.ttl" "evaluatie.ttl" "features-geometries.ttl" "selectie.ttl")
declare -a files=("alignment.ttl" "evaluatie.ttl" "selectie.ttl")


for file in "${files[@]}";
do
echo $file
riot ../examples/$file ../examples/features-geometries.ttl > /tmp/test.nt
  sparql --results=TTL --data=/tmp/test.nt  --query model.rq  > model.ttl
  rdf2dot  model.ttl | dot -Tpng > ${file/ttl/png}
  #rdf2dot  model.ttl  > model.dot
done

declare -a files=("brdr-alignment-ssn-sosa-prov.jsonld" "brdr-evaluatie-ssn-sosa-prov.jsonld" "brdr-selectie-ssn-sosa-prov.jsonld")

for file in "${files[@]}";
do
echo $file
  sparql --results=TTL --data=../examples/jsonld/$file --query model.rq  > model.ttl
  rdf2dot  model.ttl | dot -Tpng > ${file/jsonld/png}
done