
import os
from rdflib import Namespace, Graph, URIRef

from tests.use_HAP_tree.treeid import ObjectTree

BASE = "http://example.org/A#"

def get_name_from_uri(uri):
  """Extract the local name from a URI."""
  if '#' in str(uri):
    return str(uri).split('#')[-1]
  return str(uri).split('/')[-1]

def walkBrickDepthFirst(Tree, graph, root_uri):
  root_name = get_name_from_uri(root_uri)
  parent_name = root_name
  nodes = []
  triple = (root_uri,None, None )
  stack = [triple]
  while stack:
    cur_triple = stack[0]
    stack = stack[1:]
    s,p,o = cur_triple
    cur_triple = (None,None,s)
    name = get_name_from_uri(s)
    parent_name = get_name_from_uri(o)
    if name != root_name:
      Tree.addChildtoNode(name, parent_name)
    nodes.append(name)
    for t in graph.triples(cur_triple):
        stack.insert(0, t)
    # for child in reversed(self[cur_triple]["children"]):  # .get_rev_children():
    #   stack.insert(0, child)
  return nodes


if __name__ == '__main__':
  test_file1 = os.path.join(os.path.dirname(__file__), 'TEST-TREE+bricks.trig')
  test_file2 = os.path.join(os.path.dirname(__file__), 'test-tree2+bricks.ttl')
  graph1 = Graph()
  graph1.parse(test_file1, format='trig')
  graph2 = Graph()
  graph2.parse(test_file2, format='turtle')

  root_name = "A"

  graph = graph2
  for t in graph.triples((None,None,None)):
    print(t)
  root_uri = URIRef(BASE + root_name)

  Tree = ObjectTree(root_name)
  tree = walkBrickDepthFirst(Tree,graph, root_uri)
  print(tree)
  print("\n")
  for n in Tree:
    print(Tree[n])

  print("\n The generated tree:")
  Tree["tree"].printMe()
  pass
