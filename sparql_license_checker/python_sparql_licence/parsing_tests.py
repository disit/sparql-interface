#  SPARQL License Checker
#  Copyright (C) 2017 DISIT Lab http://www.disit.org - University of Florence
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import rdflib
from rdflib.plugins import sparql

from sparql_query import SparqlQuery


def clear_query(query):
    # remove trailing and starting spaces
    query = "\n".join(list(map(lambda x: x.strip(), query.splitlines())))
    # remove empty lines and spaces
    query = "\n".join(filter(lambda x: not re.match(r'^\s*$', x), query.splitlines()))
    # remove comments
    query = "\n".join(filter(lambda x: not re.match(r'^#', x), query.splitlines()))

    return query


test_queries = [
'''
prefix schema:<http://schema.org/>
SELECT DISTINCT ?name ?addr ?lat ?long ?dist WHERE {
    ?s a km4c:Service OPTION (INFERENCE "urn:ontology").
    ?s schema:name ?name.
    OPTIONAL{ ?s schema:streetAddress ?addr }
    { ?s geo:lat ?lat; geo:long ?long; 
        geo:geometry ?geo
    } UNION {
        ?s km4c:hasAccess [ geo:lat ?lat; geo:long ?long; 
        geo:geometry ?geo ] }
    BIND(bif:st_distance(?geo, bif:st_point(11.2484,43.7765)) AS ?dist)
    FILTER(?dist<=0.1)
} ORDER BY ?dist
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT DISTINCT * WHERE {
    ?s a km4c:Municipality;
    foaf:name ?l.
} ORDER BY ?l LIMIT 100
''',



'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT DISTINCT * WHERE {
    ?s a km4c:BusStop;
        foaf:name ?l;
        geo:geometry ?geo.
    BIND(bif:st_distance(?geo, bif:st_point(11.2484,43.7765)) AS ?dist)
    FILTER(?dist<=0.1)
} ORDER BY ?dist
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
prefix schema:<http://schema.org/>
SELECT DISTINCT ?name ?lat ?long ?mun WHERE {
    ?s a km4c:Service;
        schema:name ?name;
        geo:lat ?lat;
        geo:long ?long.
    ?s km4c:isInRoad/km4c:inMunicipalityOf/foaf:name ?mun
    FILTER(contains(?name, "CASA"))
}
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
prefix schema:<http://schema.org/>
SELECT DISTINCT ?name ?lat ?long ?mun WHERE {
    ?s a km4c:Service OPTION (INFERENCE "urn:ontology");
        schema:name ?name;
        geo:lat ?lat;
        geo:long ?long.
    FILTER(contains(?name, "CASA"))
} limit 100
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
prefix schema:<http://schema.org/>
SELECT DISTINCT ?name ?addr ?lat ?long ?mun WHERE {
    ?s a km4c:Service OPTION (INFERENCE "urn:ontology").
    ?s schema:name ?name.
    OPTIONAL{ ?s schema:streetAddress ?addr }
    { ?s geo:lat ?lat;
        geo:long ?long.
    } UNION {
        ?s km4c:hasAccess [ geo:lat ?lat; geo:long ?long ].
    }
    FILTER(contains(?name, "CASA"))
}
''',
'''
PREFIX km4c:<http://www.disit.org/km4city/schema#> 
PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> 
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX dcterms:<http://purl.org/dc/terms/> 
PREFIX foaf:<http://xmlns.com/foaf/0.1/> 
PREFIX skos:<http://www.w3.org/2004/02/skos/core#> 
PREFIX schema:<http://schema.org/> 
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
 
SELECT DISTINCT ?sensor ?idSensore ?lat ?long ?address ?x WHERE { 
    ?sensor rdf:type km4c:SensorSite;
        geo:lat ?lat;
        geo:long ?long; 
        dcterms:identifier ?idSensore;
        km4c:placedOnRoad ?road. 
    ?road km4c:inMunicipalityOf ?mun. 
    ?mun foaf:name "FIRENZE". 
    ?sensor schema:streetAddress ?address. 
}
''',
'''
PREFIX km4c:<http://www.disit.org/km4city/schema#> 
PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> 
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX dcterms:<http://purl.org/dc/terms/> 
PREFIX foaf:<http://xmlns.com/foaf/0.1/> 
PREFIX skos:<http://www.w3.org/2004/02/skos/core#> 
PREFIX schema:<http://schema.org/> 
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
 
SELECT DISTINCT ?sensor ?idSensore ?lat ?long ?address ?x WHERE { 
    ?sensor rdf:type km4c:SensorSite;
        geo:lat ?lat;
        geo:long ?long; 
        dcterms:identifier ?idSensore;
        schema:streetAddress ?address;
    km4c:placedOnRoad [ 
    km4c:inMunicipalityOf [ foaf:name "FIRENZE" ]].
}
''',
'''
PREFIX km4c:<http://www.disit.org/km4city/schema#>
PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms:<http://purl.org/dc/terms/>
SELECT  ?avgDistance ?avgTime ?occupancy ?concentration ?vehicleFlow ?averageSpeed ?thresholdPerc ?speedPercentile ?timeInstant WHERE{
    ?sensor rdf:type km4c:SensorSite.
    ?sensor dcterms:identifier "FI055ZTL01601".
    ?sensor km4c:hasObservation ?obs.
    ?obs km4c:measuredTime ?time.
    ?time dcterms:identifier ?timeInstant.
    OPTIONAL {?obs km4c:averageDistance ?avgDistance}
    OPTIONAL {?obs km4c:averageTime ?avgTime}
    OPTIONAL {?obs km4c:occupancy ?occupancy}
    OPTIONAL {?obs km4c:concentration ?concentration}
    OPTIONAL {?obs km4c:vehicleFlow ?vehicleFlow}
    OPTIONAL {?obs km4c:averageSpeed ?averageSpeed}
    OPTIONAL {?obs km4c:thresholdPerc ?thresholdPerc}
    OPTIONAL {?obs km4c:speedPrecentile ?speedPercentile}
} ORDER BY DESC (?timeInstant) LIMIT 1
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT ?r WHERE {
    ?n a km4c:Node;
        geo:geometry ?geo.
    BIND(bif:st_distance(?geo, bif:st_point(10.039500,44.031500)) AS ?dist)
    FILTER(?dist<=1)
    ?n (^km4c:startsAtNode | ^km4c:endsAtNode)/^km4c:containsElement ?r.
} ORDER BY ?dist limit 1
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT ?r ?name ?m WHERE {
    ?n a km4c:Node;
        geo:geometry ?geo.
    BIND(bif:st_distance(?geo, bif:st_point(10.039500,44.031500)) AS ?dist)
    FILTER(?dist<=1)
    ?n (^km4c:startsAtNode | ^km4c:endsAtNode)/^km4c:containsElement ?r.
    ?r km4c:extendName ?name.
    ?r km4c:inMunicipalityOf/foaf:name ?m
} ORDER BY ?dist limit 1
''',
'''
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT ?r ?name ?m WHERE {
    ?n a km4c:Node;
        geo:geometry ?geo.
    BIND(bif:st_distance(?geo, bif:st_point(10.039500,44.031500)) AS ?dist)
    FILTER(?dist<=1)
    ?n (^km4c:startsAtNode | ^km4c:endsAtNode)/^km4c:containsElement ?r.
    ?r km4c:extendName ?name.
    ?r km4c:inMunicipalityOf [foaf:name ?m]
} ORDER BY ?dist limit 1
''',
'''
DEFINE input:inference 'urn:ontology'
PREFIX km4c: <http://www.disit.org/km4city/schema#>
PREFIX schema:<http://schema.org/>
SELECT DISTINCT ?s ?name ?addr ?lat ?long ?dist WHERE {
    ?s a km4c:Service;
        schema:name ?name.
    OPTIONAL{ ?s schema:streetAddress ?addr }
    {
        ?s geo:lat ?lat; geo:long ?long; geo:geometry ?geo
    } UNION {
        ?s km4c:hasAccess [ geo:lat ?lat; geo:long ?long; geo:geometry ?geo ]
    }
    BIND(bif:st_distance(?geo, bif:st_point(11.2484,43.7765)) AS ?dist)
    FILTER(?dist<=0.1)
} ORDER BY ?dist
''',
'''
SELECT distinct ?s
WHERE {
    graph <http://www.disit.org/km4city/resource/Sensori/sensori_EMPOLI> {?s ?p ?o}
}
LIMIT 100
''',
'''
SELECT distinct ?g
WHERE {
    graph ?g {<http://www.disit.org/km4city/resource/FIPILIM000402> ?p ?o}
}
LIMIT 100
''',
'''
SELECT distinct ?g ?s ?p ?o
FROM <http://www.disit.org/km4city/resource/Sensori/sensori_EMPOLI>
FROM <http://www.disit.org/km4city/resource/Sensori/sensori_FIRENZE>
WHERE {
    ?s a km4c:SensorSite.
    graph ?g {?s ?p ?o}
}
''',
'''
SELECT distinct ?g ?s ?p ?o
FROM <http://www.disit.org/km4city/resource/Sensori/sensori_EMPOLI>
FROM <http://www.disit.org/km4city/resource/Sensori/sensori_FIRENZE>
FROM NAMED <http://www.disit.org/km4city/resource/Sensori/sensori_EMPOLI>
FROM NAMED <http://www.disit.org/km4city/resource/Sensori/sensori_FIRENZE>
WHERE {
    ?s a km4c:SensorSite.
    graph ?g {?s ?p ?o}
} LIMIT 100
'''
]

i=0
for source_query in test_queries:
    i+=1
    parsed_query = sparql.parser.parseQuery(clear_query(source_query))
    sparql_query = SparqlQuery()
    sparql_query.init_from_parsed_tree(parsed_query)

    print('##################################################################')
    print("TEST: QUERY " + str(i))
    print('------------------')
    print(str(sparql_query))
