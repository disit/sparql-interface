$(document)
		.ready(
				function() {
					var sampleQuery1 = "PREFIX km4cr: <http://www.disit.org/km4city/schema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nSELECT * WHERE {\n   ?s a km4cr:Municipality;\n      rdfs:label ?l.\n} ORDER BY ?l";
					var sampleQuery2 = "PREFIX km4cr: <http://www.disit.org/km4city/schema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX omgeo: <http://www.ontotext.com/owlim/geo#>\nSELECT * WHERE {\n   ?s a km4cr:BusStop;\n      rdfs:label ?l;\n      omgeo:nearby(\"43.7765\" \"11.2484\" \"0.1km\")\n} ORDER BY ?l\nLIMIT 50";

					var flintConfig = {
						"interface" : {
							"toolbar" : true,
							"menu" : true
						},
						"namespaces" : [
								{
									"name" : "Knowledge Model 4 City",
									"prefix" : "mk4c",
									"uri" : "http://www.disit.org/km4city/schema#"
								},
								{
									"name" : "Friend of a friend",
									"prefix" : "foaf",
									"uri" : "http://xmlns.com/foaf/0.1/"
								},
								{
									"name" : "XML schema",
									"prefix" : "xsd",
									"uri" : "http://www.w3.org/2001/XMLSchema#"
								},
								{
									"name" : "SIOC",
									"prefix" : "sioc",
									"uri" : "http://rdfs.org/sioc/ns#"
								},
								{
									"name" : "Resource Description Framework",
									"prefix" : "rdf",
									"uri" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
								},
								{
									"name" : "Resource Description Framework schema",
									"prefix" : "rdfs",
									"uri" : "http://www.w3.org/2000/01/rdf-schema#"
								},
								{
									"name" : "Dublin Core",
									"prefix" : "dc",
									"uri" : "http://purl.org/dc/elements/1.1/"
								},
								{
									"name" : "Dublin Core terms",
									"prefix" : "dct",
									"uri" : "http://purl.org/dc/terms/"
								},
								{
									"name" : "Creative Commons",
									"prefix" : "cc",
									"uri" : "http://www.creativecommons.org/ns#"
								},
								{
									"name" : "Web Ontology Language",
									"prefix" : "owl",
									"uri" : "http://www.w3.org/2002/07/owl#"
								},
								{
									"name" : "Simple Knowledge Organisation System",
									"prefix" : "skos",
									"uri" : "http://www.w3.org/2004/02/skos/core#"
								},
								{
									"name" : "Geography",
									"prefix" : "geo",
									"uri" : "http://www.w3.org/2003/01/geo/wgs84_pos#"
								},
								{
									"name" : "Geonames",
									"prefix" : "geonames",
									"uri" : "http://www.geonames.org/ontology#"
								},
								{
									"name" : "DBPedia property",
									"prefix" : "dbp",
									"uri" : "http://dbpedia.org/property/"
								},
								{
									"name" : "Open Provenance Model Vocabulary",
									"prefix" : "opmv",
									"uri" : "http://purl.org/net/opmv/ns#"
								},
								{
									"name" : "Functional Requirements for Bibliographic Records",
									"prefix" : "frbr",
									"uri" : "http://purl.org/vocab/frbr/core#"
								}

						],
						"defaultEndpointParameters" : {
							"queryParameters" : {
								"format" : "output",
								"query" : "query",
								"update" : "update"
							},
							"selectFormats" : [ {
								"name" : "SPARQL-XML",
								"format" : "sparql",
								"type" : "application/sparql-results+xml"
							}, {
								"name" : "JSON",
								"format" : "json",
								"type" : "application/sparql-results+json"
							} ],
							"constructFormats" : [ {
								"name" : "Plain text",
								"format" : "text",
								"type" : "text/plain"
							}, {
								"name" : "RDF/XML",
								"format" : "rdfxml",
								"type" : "application/rdf+xml"
							}, {
								"name" : "Turtle",
								"format" : "turtle",
								"type" : "application/turtle"
							} ]
						},
						"endpoints" : [
								{
									"name" : "KM4CITY",
									"uri" : "http://192.168.0.205:8080/openrdf-sesame/repositories/km4city36",
									"modes" : ["sparql11query"],
									queries : [
											{
												"name" : "All municipalities",
												"description" : "Select all municipalities names.",
												"query" : sampleQuery1
											},
											{
												"name" : "Bus stops near the Florence SMN train station",
												"description" : "The bus stops within 100m of the Firenze SMN ",
												"query" : sampleQuery2
											} ]
								},
								{
									"name" : "ECLAP",
									"uri" : "http://www.eclap.eu/sparql",
									"modes" : ["sparql11query"],
								},
								{
									"name" : "OSIM",
									"uri" : "http://openmind.disit.org:8080/openrdf-sesame/repositories/osim-rdf-store",
									"modes" : ["sparql11query"],
								},
            ],
						"defaultModes" : [ {
							"name" : "SPARQL 1.0",
							"mode" : "sparql10"
						}, {
							"name" : "SPARQL 1.1 Query",
							"mode" : "sparql11query"
						}, {
							"name" : "SPARQL 1.1 Update",
							"mode" : "sparql11update"
						} ],

						"licenseCheckerConfig" : {
							"pythonServer" : "http://127.0.0.1:5000/"
						}
					}

					var flintEd = new FlintEditor("flint-editor",
							"sparql/images", flintConfig);
				});
