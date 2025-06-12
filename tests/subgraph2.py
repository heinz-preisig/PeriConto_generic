from rdflib import Graph
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD

RDFSTerms = {
        "class"        : RDFS.Class,
        "is_class"     : RDF.type,  # was "is_type"
        "is_member"    : RDFS.member,
        "is_defined_by": RDFS.isDefinedBy,
        "value"        : RDF.value,
        "data_type"    : RDFS.Datatype,
        "comment"      : RDFS.comment,
        "integer"      : XSD.integer,
        "string"       : XSD.string,
        "decimal"      : XSD.decimal,
        "uri"          : XSD.anyURI,
        "label"        : RDFS.label,
        "boolean"      : XSD.boolean,
        }
# Load the RDF graph
g = Graph()
g.parse("test.trig", format="turtle")

predicates = set()
for s, p, o in g.triples((None, None, None)):
  predicates.add(p)
  if "SECOND" in s:
    root = s


#
# # Define the root node
# root = URIRef("http://example.org/root")


# g.add((EX.A, EX.hasChild, EX.B))
# g.add((EX.A, EX.hasPart, EX.C))
# g.add((EX.B, EX.hasChild, EX.D))
# g.add((EX.B, EX.relatedTo, EX.E))
# g.add((EX.C, EX.hasChild, EX.F))

# Define the predicates that define the tree structure
# tree_predicates = [
#     URIRef("http://example.org/hasChild"),
#     URIRef("http://example.org/hasPart"),
#     URIRef("http://example.org/relatedTo")
# ]

# Recursive function to find all connected nodes
def get_subtree(graph, node, predicates):
  subtree = {node}
  for predicate in predicates:

    for s, p, o in graph.triples((None, predicate, node)):
      child = s

      if child not in subtree:  # Avoid duplicate processing
        print("child", child)
        subtree.update(get_subtree(graph, child, predicates))
  return subtree


# Get all subtree nodes
print("root", root)
subtree_nodes = get_subtree(g, root, predicates)

# Print subtree nodes
for node in subtree_nodes:
  print(node)
