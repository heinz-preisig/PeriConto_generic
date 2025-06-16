


import os
from rdflib import Namespace, Graph, URIRef
from typing import List

from treeid import ObjectTree

BASE = "http://example.org/A#"

def get_name_from_uri(uri):
  """Extract the local name from a URI."""
  if '#' in str(uri):
    return str(uri).split('#')[-1]
  return str(uri).split('/')[-1]



def extract_path_names(path):
  path_names = []
  for p in path:
    _, name = p.split("#")
    path_names.append(name)
  return path_names

def get_all_paths_by_name(graph, start, target):
  paths = find_all_paths(graph, start, target)
  path_names = []
  for p in paths:
    path_names.append(extract_path_names(p))
  return path_names


def find_all_paths(graph: Graph, start: URIRef, target: URIRef, max_depth: int = 20) -> List[List[URIRef]]:
  """
    Find all paths from a start node to a target node in an RDF graph using depth-first search.

    Args:
        graph (Graph): The RDF graph to traverse.
        start (URIRef): The starting node for pathfinding.
        target (URIRef): The target node to reach.
        max_depth (int): The maximum depth to search, default is 20.

    Returns:
        List[List[URIRef]]: A list of paths, where each path is a list of nodes from start to target.
  """
  paths = []

  def dfs(current, path, depth):
    if depth > max_depth:
      return
    path.append(current)
    if current == target:
      paths.append(path.copy())
    else:
      for _, _, obj in graph.triples((current, None, None)):
        dfs(obj, path, depth + 1)
    path.pop()

  dfs(start, [], 0)
  return paths

def find_all_leaves(graph):
  subjects = set()
  objects = set()
  for s,p,o in graph.triples((None, None, None)):
    subjects.add(s)
    objects.add(o)
  leaves = subjects - objects
  return leaves


if __name__ == '__main__':
  test_file1 = os.path.join(os.path.dirname(__file__), 'TEST-TREE+bricks.trig_')
  test_file2 = os.path.join(os.path.dirname(__file__), 'test-tree2+bricks.ttl')
  graph1 = Graph()
  graph1.parse(test_file1, format='turtle')
  graph2 = Graph()
  graph2.parse(test_file2, format='turtle')

  root_name = "A"

  graph = graph1
  for t in graph.triples((None,None,None)):
    print(t)
  root_uri = URIRef(BASE + root_name)

  leaves = find_all_leaves(graph)
  print("\nleaves:\n",leaves)

  target = root_uri
  paths = {}
  for start in leaves:
    paths[start] = get_all_paths_by_name(graph, start, target)

  print(paths)
  print("\n")

  Tree = ObjectTree(root_name)
  parent = root_name

  for leave in paths:
    for path in paths[leave]:
      for i in reversed(path):
        if not Tree.hasChild(parent, i) and i != root_name:
          Tree.addChildtoNode(i, parent)
        parent = i
      print(path)


  print(Tree)
  print("\n")
  for n in Tree:
    print(Tree[n])

  print("\n The generated tree:")
  Tree["tree"].printMe()
  pass
