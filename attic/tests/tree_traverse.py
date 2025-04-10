from rdflib import Graph, URIRef

def depth_first_traversal(graph, start_node, visited=None, depth=0):
    if visited is None:
        visited = set()

    print("  " * depth + f"{start_node.split('#')[-1]}")
    visited.add(start_node)

    for _, predicate, obj in graph.triples((start_node, None, None)):
        if isinstance(obj, URIRef) and obj not in visited:
            depth_first_traversal(graph, obj, visited, depth + 1)

g = Graph()
g.parse(data='''
@prefix ABC: <http://example.org/ABC#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ABC: xsd:integer ABC:Int ;
    xsd:string ABC:S .

ABC:Ab rdfs:member ABC:A .

ABC:B a ABC:Class .
    
ABC:K rdfs:isDefinedBy ABC:B .
    
ABC:L rdfs:isDefinedBy ABC:B .

ABC:Int rdf:value ABC:A .

ABC:K rdfs:member ABC:ABC .

ABC:L rdfs:member ABC:ABC .

ABC:S rdf:value ABC:B .

ABC:A rdfs:member ABC:ABC .

ABC:ABC a ABC:Class .
''', format='turtle')

start = URIRef('http://example.org/ABC#ABC')
depth_first_traversal(g, start)
