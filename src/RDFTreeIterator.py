from rdflib import Graph
from rdflib import Namespace

from object_tree_plot import plot_tree_graphviz
from treeid import ObjectTree

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

g2 = Graph()
g2.parse(data="""
@prefix ABC: <http://example.org/ABC#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ABC: xsd:integer ABC:Int .

ABC:C rdfs:member ABC:B .

ABC:ABC a ABC:Class .

ABC:B rdfs:member ABC:A .

ABC:Int rdf:value ABC:A .

ABC:L rdfs:member ABC:A .

ABC:A a ABC:Class ;
    rdfs:isDefinedBy ABC:L ;
    rdfs:member ABC:ABC .
""")

g3 = Graph()
g3.parse(data="""
@prefix ABC: <http://example.org/ABC#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ABC: xsd:integer ABC:Int ;
    xsd:string ABC:S .

ABC:Ab rdfs:member ABC:A .

ABC:B a ABC:Class ;
    rdfs:isDefinedBy ABC:Ab,
        ABC:K,
        ABC:L .

ABC:Int rdf:value ABC:A .

ABC:K rdfs:member ABC:ABC .

ABC:L rdfs:member ABC:ABC .

ABC:S rdf:value ABC:B .

ABC:A rdfs:member ABC:ABC .

ABC:ABC a ABC:Class .
""")


def getName(iri):
  return iri.split("#")[-1]


def depth_first_iter(graph, node, in_branch_visited=None, branch=None, current_branch=None, parent=None, depth=0):
  if not parent :
    # parent = getName(node)
    parent = node
  if not in_branch_visited:
    in_branch_visited = set()
  if not branch:
    branch = set()
  if not current_branch:
    current_branch = getName(node)


  yield (depth, node, current_branch, parent)
  in_branch_visited.add(node)

  for child, p, target in sorted(graph.triples((None, None, node)), key=lambda t: t[0].split('#')[-1]):
    if child not in in_branch_visited:
      # parent = getName(target)
      parent = target
      if p == RDFS.isDefinedBy:
        branch.add(target)
        current_branch = getName(target)
        yield from depth_first_iter(graph, child, in_branch_visited=set(), branch=branch, current_branch=current_branch, parent=parent, depth=depth + 1)
      else:
        yield from depth_first_iter(graph, child, in_branch_visited=in_branch_visited, branch=branch, current_branch=current_branch, parent=parent, depth=depth + 1)



tree = ObjectTree(ABC.ABC)
# Example usage:
for depth, node, current_branch, parent in depth_first_iter(g3, ABC.ABC):
  # print(current_branch, parent)
  # print("  " * depth + node.split('#')[-1])
  tree.addChildtoNode(node,parent)
  print(parent, node)

print(tree)

# output:
# g::
# ABC
#     A
#         Ab
#         Int
#
#     K
#         B
#             S
#
#     L
#         B
#             S

# g3::
# ABC
#   A
#       Ab
#           B
#               S
#
#       Int
#
#   K
#       B
#           S
#
#   L
#       B
#           S


# g2::
# ABC
#   A
#       Ab
#           B
#               S
#
#       Int
#
#   C
#       B
#           S

dot = plot_tree_graphviz(tree)
dot.render(view=True)