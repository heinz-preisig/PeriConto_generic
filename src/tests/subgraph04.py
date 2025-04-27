from rdflib import Graph, Namespace
from graphviz import Digraph

ABC = Namespace("http://example.org/ABC#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# Load RDF graph
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

# Create a Graphviz Digraph
dot = Digraph(comment='RDF Tree')
dot.attr('node', shape='ellipse')

def depth_first(graph, node, in_branch_visited=None, branch=None, parent=None):
    if in_branch_visited is None:
        in_branch_visited = set()
    if branch is None:
        branch = set()

    label = node.split('#')[-1]
    dot.node(label)
    if parent:
        dot.edge(parent, label)

    in_branch_visited.add(node)

    for child, p, target in sorted(graph.triples((None, None, node)), key=lambda t: t[0].split('#')[-1]):
        if child not in in_branch_visited:
            if p == RDFS.isDefinedBy:
                branch.add(node)
                depth_first(graph, child, in_branch_visited=set(), branch=branch, parent=label)
            else:
                depth_first(graph, child, in_branch_visited=in_branch_visited, branch=branch, parent=label)

# Start the traversal and tree building
depth_first(g, ABC.ABC)

# Render to file
dot.render('rdf_tree', view=True, format='png')  # will generate rdf_tree.png and open it
