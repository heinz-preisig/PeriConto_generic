from rdflib import Graph, URIRef, Namespace

ABC = Namespace("http://example.org/ABC#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

# RDF data
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


def depth_first(graph, node, in_branch_visited=None, branch=None, depth=0):
  if in_branch_visited is None:
    in_branch_visited = set()
  if branch is None:
    branch = set()

  print("  " * depth + node.split('#')[-1])
  in_branch_visited.add(node)

  # Traverse incoming rdfs:member
  for child, p, node in sorted(graph.triples((None, None, node)), key=lambda t: t[0].split('#')[-1]):
    if child not in in_branch_visited:
      if p == RDFS.isDefinedBy:
        # traverse_branch(graph, child, in_branch_visited, set(), depth + 1)
        branch.add(node)
        depth_first(graph, child, in_branch_visited=set(), branch=branch, depth=depth + 1)
      else:
        depth_first(graph, child, in_branch_visited=in_branch_visited, branch=branch, depth=depth + 1)



# Run the traversal
depth_first(g, ABC.ABC)