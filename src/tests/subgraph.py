from rdflib import Graph, URIRef, Namespace

EX = Namespace("http://example.org/")

# Load the RDF graph
g = Graph()
# g.parse("example.rdf", format="turtle")

# Define the root node
# root = URIRef("http://example.org/root")

g.add((EX.A, EX.hasChild, EX.B))
g.add((EX.A, EX.hasChild, EX.C))
g.add((EX.B, EX.hasChild, EX.D))
g.add((EX.B, EX.hasChild, EX.E))
g.add((EX.C, EX.hasChild, EX.F))

# Find all descendants recursively
def get_subtree(graph, node, predicate):
    subtree = {node}
    for _, _, child in graph.triples((node, None, None)):
        subtree.update(get_subtree(graph, child, predicate))
    return subtree

subtree_nodes = get_subtree(g, EX.B, URIRef("http://example.org/hasChild"))

# Print subtree nodes
for node in subtree_nodes:
    print(node)
