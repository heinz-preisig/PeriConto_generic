from rdflib import Graph, URIRef, Literal


def depth_first_traversal(graph, start_node, visited=None, depth=0):
  if visited is None:
    visited = set()

  # Print the current node with the depth indentation
  print("  " * depth + f"{start_node.split('#')[-1]}")
  visited.add(start_node)

  # Traverse forward (start_node -> objects)
  for _, predicate, obj in graph.triples((start_node, None, None)):
    if isinstance(obj, URIRef) and obj not in visited:
      # print("  " * (depth + 1) + f"Object: {obj.split('#')[-1]}")  # Print the object for clarity
      depth_first_traversal(graph, obj, visited, depth + 1)
    elif isinstance(obj, Literal):  # Handle literals
      print("  " * (depth + 1) + f"Literal: {obj}")

  # Traverse reverse (subject -> start_node)
  for subj, predicate, _ in graph.triples((None, None, start_node)):
    if subj not in visited:
      # print("  " * (depth + 1) + f"Subject: {subj.split('#')[-1]}")  # Print the subject for clarity
      depth_first_traversal(graph, subj, visited, depth + 1)


# Create an RDF graph
g = Graph()
g.parse(data='''
@prefix ABC: <http://example.org/ABC#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ABC: xsd:integer ABC:Int ;
    xsd:string ABC:S .

ABC:Ab rdfs:member ABC:A .

ABC:B a ABC:Class ;
    rdfs:isDefinedBy ABC:K,
        ABC:L .

ABC:Int rdf:value ABC:A .

ABC:K rdfs:member ABC:ABC .

ABC:L rdfs:member ABC:ABC .

ABC:S rdf:value ABC:B .

ABC:A rdfs:member ABC:ABC .

ABC:ABC a ABC:Class .
''', format='turtle')

# Define the starting point of traversal
start = URIRef('http://example.org/ABC#ABC')

# Perform depth-first traversal
depth_first_traversal(g, start)
