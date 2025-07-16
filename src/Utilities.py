import os
from typing import Any

from graphviz import Digraph
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from BricksAndTreeSemantics import RULES

DEBUGG = False


def camelCase(sentence):
  camel = sentence.title().replace(" ", "")
  return camel


def classCase(word):
  classCase = word.upper()
  return classCase


def debugging(*info):
  if DEBUGG:
    print("debugging", info)


def getName(iri):
  return iri.split("#")[-1]


RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


def depth_first_iter(graph, start_node):
  """
  Iterative depth-first search that handles branches properly.

  Args:
      graph: The RDF graph to traverse
      start_node: The node to start traversal from

  Yields:
      Tuples of (depth, node, current_branch, parent, predicate, node_id, parent_id)
  """
  # Stack items are (node, parent, depth, current_branch, visited_in_branch, is_new_branch, predicate, parent_id, node_id)
  # We'll track visited nodes per branch to allow the same node in different branches
  stack = [(start_node, None, 0, getName(start_node), set(), False, None, -1, 1)]
  # Dictionary to store node to ID mapping
  node_to_id = {str(start_node): 1}
  # Counter for unique IDs
  next_id = 2

  while stack:
    node, parent, depth, current_branch, visited, is_new_branch, predicate, parent_id, node_id = stack.pop()

    # Create a unique key for this node in the current branch context
    node_key = str(node)

    # Skip if we've already visited this node in the current branch
    if node_key in visited:
      continue

    # If this is a new node, assign it an ID
    if node_key not in node_to_id:
      node_to_id[node_key] = next_id
      next_id += 1

    # Get the actual node ID
    current_node_id = node_to_id[node_key]

    # Mark as visited in this branch
    visited.add(node_key)

    # Yield current node with predicate and IDs
    yield (depth, node, current_branch, parent, predicate, current_node_id, parent_id)

    # Get all children with their predicates
    children = []
    try:
      for s, p, o in graph.triples((None, None, node)):
        key = str(s).split('#')[-1] if '#' in str(s) else str(s)
        children.append((s, p, o, key))
    except Exception as e:
      print(f"Error processing node {node}: {e}")
      continue

    # Sort children in reverse order to maintain correct traversal order when using stack
    children.sort(key=lambda x: x[3], reverse=True)

    # Process children
    for child, p, target, _ in children:
      child_key = str(child)
      # Skip if this would create a cycle
      if child_key == node_key:
        continue

      # Get or assign an ID to the child
      if child_key not in node_to_id:
        node_to_id[child_key] = next_id
        next_id += 1

      if p == RDFS.isDefinedBy:
        # New branch - start with fresh visited set
        stack.append((child, node, depth + 1, getName(target), set(), True, p, current_node_id, node_to_id[child_key]))
      else:
        # Same branch - pass down the visited set
        branch_visited = set(visited)  # Copy to avoid modifying parent's visited set
        stack.append((child, node, depth + 1, current_branch, branch_visited, False, p, current_node_id, node_to_id[child_key]))


def breadth_first_iter(graph, start_node):
  """
  Iterative breadth-first search that handles branches properly.

  Args:
      graph: The RDF graph to traverse
      start_node: The node to start traversal from

  Yields:
      Tuples of (depth, node, current_branch, parent, predicate, node_id, parent_id)
  """
  from collections import deque

  # Queue items are (node, parent, depth, current_branch, visited_in_branch, is_new_branch, predicate, parent_unique_id)
  # We'll track visited nodes per branch to allow the same node in different branches
  queue = deque()
  queue.append((start_node, None, 0, getName(start_node), set(), False, None, -1))
  unique_id = 0

  while queue:
    node, parent, depth, current_branch, visited, is_new_branch, predicate, parent_unique_id = queue.popleft()

    # Create a unique key for this node in the current branch context
    node_key = str(node)

    # Skip if we've already visited this node in the current branch
    if node_key in visited:
      continue

    # Mark as visited in this branch
    visited.add(node_key)

    unique_id += 1

    # Yield current node with predicate
    yield (depth, node, current_branch, parent, predicate, unique_id, parent_unique_id)

    # Get all children with their predicates
    children = []
    try:
      for s, p, o in graph.triples((None, None, node)):
        key = str(s).split('#')[-1] if '#' in str(s) else str(s)
        children.append((s, p, o, key))
    except Exception as e:
      print(f"Error processing node {node}: {e}")
      continue

    # Sort children to maintain consistent order
    children.sort(key=lambda x: x[3])

    # Process children
    for child, p, target, _ in children:
      child_key = str(child)
      # Skip if this would create a cycle
      if child_key == node_key:
        continue

      if p == RDFS.isDefinedBy:
        # New branch - start with fresh visited set
        queue.append((child, node, depth + 1, getName(target), set(), True, p, unique_id))
      else:
        # Same branch - pass down the visited set
        # But allow revisiting nodes that are in different branches
        branch_visited = set(visited)  # Copy to avoid modifying parent's visited set
        queue.append((child, node, depth + 1, current_branch, branch_visited, False, p, unique_id))


def getFilesAndVersions(abs_name, ext):
  base_name = os.path.basename(abs_name)
  ver = 0  # initial last version
  _s = []
  directory = os.path.dirname(abs_name)
  files = os.listdir(directory)

  for f in files:
    n, e = os.path.splitext(f)
    #        print "name", n
    if e == ext:  # this is another type
      if n[0:len(base_name) + 1] == base_name + "(":  # only those that start with name
        #  extract version
        l = n.index("(")
        r = n.index(")")
        assert l * r >= 0  # both must be there
        v = int(n[l + 1:r])
        ver = max([ver, v])
        _s.append(n)
  return _s, ver


def saveBackupFile(path):
  ver_temp = "(%s)"
  (abs_name, ext) = os.path.splitext(path)  # path : directory/<name>.<ext>
  if os.path.exists(path):
    _f, ver = getFilesAndVersions(abs_name, ext)
    old_path = path
    new_path = abs_name + ver_temp % str(ver + 1) + ext
    next_path = abs_name + ver_temp % str(ver + 2) + ext
    os.rename(old_path, new_path)
    return old_path, new_path, next_path


# def find_all_paths(graph: Graph, start: URIRef, target: URIRef, max_depth: int = 20) -> tuple[list[Any], list[Any]]:
#   """
#     Find all paths from a start node to a target node in an RDF graph using depth-first search.
#
#     Args:
#         graph (Graph): The RDF graph to traverse.
#         start (URIRef): The starting node for pathfinding.
#         target (URIRef): The target node to reach.
#         max_depth (int): The maximum depth to search, default is 20.
#
#     Returns:
#         List[List[URIRef]]: A list of paths, where each path is a list of nodes from start to target.
#   """
#   paths = []
#   properties = []
#
#   def dfs(current, current_property, path, properties,depth):
#     if depth > max_depth:
#       return
#     path.append(current)
#     if current == target:
#       paths.append(path.copy())
#       properties.append(current_property)
#     else:
#       for _, p, obj in graph.triples((current, None, None)):
#         prop = p.split("#")[1]
#         properties.append(prop)
#         dfs(obj, prop, path, properties, depth + 1)
#     path.pop()
#     properties.pop()
#
#   dfs(start, "class",[], [], 0)
#   return paths, properties

def find_all_paths(graph: Graph, property, start: URIRef, target: URIRef, max_depth: int = 20) -> tuple[list[Any], list[dict]]:
  paths = []
  all_properties = []  # This will store a list of property dictionaries for each path

  def dfs(current, current_path, current_props, depth):
    if depth > max_depth:
      return
    if current == target:
      paths.append(current_path + [current])
      all_properties.append(dict(current_props))  # Convert list of tuples to dict
      return
    for s, p, obj in graph.triples((current, None, None)):
      object_name = s.split("#")[1] if "#" in obj else str(obj)
      prop = p.split("#")[1] if "#" in p else str(p)
      # Store the property for this object in the current path
      props = current_props + [(object_name, prop)]
      dfs(obj, current_path + [current], props, depth + 1)

  # Start with empty path and properties
  start_name = start.split("#")[1] if "#" in start else str(start)
  property_name = property.split("#")[1] if "#" in property else str(property)
  dfs(start, [], [(start_name, property_name)], 0)
  return paths, all_properties


def extract_path_names(path):
  path_names = []
  for p in path:
    _, name = p.split("#")
    path_names.append(name)
  return path_names


def get_all_paths_by_name(graph, property, start, target):
  paths, properties = find_all_paths(graph, property, start, target)
  path_names = []
  for p in paths:
    path_names.append(extract_path_names(p))
  return path_names, properties


def find_all_leaves(graph):
  subjects = set()
  objects = set()
  predicates = {}
  for s, p, o in graph.triples((None, None, None)):
    subjects.add(s)
    objects.add(o)
    predicates[s] = p
  leaves = subjects - objects
  properties = {}
  for s in predicates:
    if s in leaves:
      o_name = s.split("#")[1]
      properties[o_name] = predicates[s]

  return leaves, properties


def find_path_back_triples(graph, leave_triple, root):
  """
  Find a path from a primitive, which is a leave to the root.
  It's a straight walk back to the root, as it is a tree, but
  one has to watch out for multiple equal leave values.
  Remedy: extract names without duplicating a name -- rule: names in a path are unique
          and then build path again.
  """
  from BricksAndTreeSemantics import RDF_PRIMITIVES, RDFSTerms

  path = [leave_triple]
  now = path[0][2]  # neighbour

  while not now == root:
    triple = (now, None, None)
    for s, p, o in graph.triples(triple):
      t = (s, p, o)
      if (t not in path):
        if not p in RDF_PRIMITIVES and o not in RDFSTerms["class"]:
          now = o
          path.append(t)

  path_names = []
  for _s, _p, _o in path:
    pre, n_s = _s.split("#")
    if n_s not in path_names:
      path_names.append(n_s)
  root_name = root.split("#")[1]
  path_names.append(root_name)

  reduced_path = []
  for _s, _p, _o in path:
    _, n_o = _o.split("#")
    if n_o in path_names:
      reduced_path.append((_s, _p, _o))

  return reduced_path, path_names


def get_subtree(graph, node, predicates):
  subtree = {node}
  # print("node ", node)
  for predicate in predicates:
    for child, _, _ in graph.triples((None, predicate, node)):
      # print("child", child)
      if child not in subtree:  # Avoid duplicate processing
        subtree.update(get_subtree(graph, child, predicates))
  return subtree


EDGE_COLOURS = {
        "is_class"     : "red",
        "is_member"    : "blue",
        "is_defined_by": "darkorange",
        "value"        : "black",
        "data_type"    : "green",
        # "comment"         : "green",
        # "integer"         : "darkorange",
        # "string"          : "cyan",
        "other"        : "orange",
        }

NODE_SPECS = {
        "Class"      : {
                "colour"   : "red",
                "shape"    : "rectangle",
                "fillcolor": "red",
                "style"    : "filled",
                },
        "member"     : {
                "colour"   : "orange",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "value"      : {
                "colour"   : "green",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "integer"    : {
                "colour"   : "blue",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "string"     : {
                "colour"   : "blue",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "boolean"    : {
                "colour"   : "blue",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        # "ROOT"       : {
        #         "colour"   : "red",
        #         "shape"    : "rectangle",
        #         "fillcolor": "white",
        #         "style"    : "filled",
        #         },
        # "link"       : {
        #         "colour"   : "green",
        #         "shape"    : "rectangle",
        #         "fillcolor": "white",
        #         "style"    : "filled",
        #         },
        "isDefinedBy": {
                "colour"   : "red",
                "shape"    : "rectangle",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "other"      : {
                "colour"   : None,
                "shape"    : None,
                "fillcolor": "red",
                "style"    : None,
                },
        }
NODE_SPECS["linked"] = NODE_SPECS["Class"]


class TreePlot:
  """
    Create Digraph plot
  """

  def __init__(self, graph_name, graph_triples, class_names):

    self.graph_name = graph_name
    self.classes = class_names
    self.triples = graph_triples
    self.dot = Digraph(graph_name)
    self.dot.graph_attr["rankdir"] = "LR"  # Set graph direction Left to Right
    # self.dot.graph_attr["label"] = "Graph of : %s"%graph_name  # Add a title
    # self.dot.graph_attr["labelloc"] = "t"  # Position title at the top
    # self.dot.graph_attr["fontsize"] = "16"  # Adjust font size of the title

    self.nodes = set()

  def addNode(self, node, type):
    print("plot", node, type)
    try:
      specs = NODE_SPECS[type]
    except:
      specs = NODE_SPECS["other"]

    self.dot.node(node,
                  color=specs["colour"],
                  shape=specs["shape"],
                  fillcolor=specs["fillcolor"],
                  style=specs["style"],
                  )
    self.nodes.add(node)

  def addEdge(self, From, To, type, dir):
    try:
      colour = EDGE_COLOURS[type]
    except:
      colour = EDGE_COLOURS["other"]
    if dir == 1:
      self.dot.edge(From, To,
                    color=colour,
                    label=type
                    )
    elif dir == -1:
      self.dot.edge(To, From,
                    color=colour,
                    label=type
                    )
    else:
      print(">>>>>>>>>>>>>>>> should not come here")

  def makeMe(self, root):
    self.addNode(root, "Class")

    nodes = set()
    new_triples = []

    for q in self.triples:
      s, p, o, dir = q
      if ":" in s:
        s = s.split(":")[-1]
      if ":" in o:
        o = o.split(":")[-1]
      new_triples.append((s, p, o, dir))
      nodes.add((s, p))
      # nodes.add((o, p))

    for n, p in nodes:
      type = RULES[p]
      self.addNode(n, type)

    for q in new_triples:
      s, p, o, dir = q
      self.addEdge(s, o, p, dir)

    no_nodes = len(self.nodes)

    self.dot.graph_attr["label"] = "Graph of : %s with %s nodes\n" % (self.graph_name, no_nodes)  # Add a title
    self.dot.graph_attr["labelloc"] = "t"  # Position title at the top
    self.dot.graph_attr["fontsize"] = "20"  # Adjust font size of the title
    self.dot.graph_attr["ranksep"] = "1.5"
    print("number of nodes:", no_nodes)


if __name__ == "__main__":
  # Example RDF Graph
  from rdflib import Graph, URIRef
  from BricksAndTreeSemantics import RDFSTerms

  # data = '''
  #     @prefix ex: <http://example.org/> .
  #     ex:A ex:knows ex:B .
  #     ex:B ex:knows ex:C .
  #     ex:C ex:knows ex:D .
  # '''
  # g.parse(data=data, format="turtle")
  #
  # start_node = URIRef("http://example.org/A")
  # end_node = URIRef("http://example.org/D")

  data3 = """
  @prefix k: <http://example.org/k> .
  @prefix k_I: <http://example.org/k#> .
  @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
  @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
  @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
  
  k: a rdfs:Class .  
  "" xsd:boolean k_I:b .  
  "123" xsd:integer k_I:i .  
  k_I:b rdf:value k: .  
  k_I:i rdf:value k_I:item11 .  
  k_I:item1 rdfs:member k: .  
  k_I:item11 rdfs:member k_I:item1 .  
  """

  # print("============================================================")
  # g2 = Graph()
  # g2.parse(data=data3, format="turtle")
  #
  # root = URIRef("http://example.org/k")
  # neighbour = URIRef("http://example.org/k#i")
  # leave = Literal("123")
  #
  # triple = (neighbour, RDFSTerms["integer"], leave)
  # triple_ = (leave, RDFSTerms["integer"], neighbour)
  #
  # path = find_path_back_triples(g2, triple_, root)
  # for t in path:
  #   print(t)

  # print("============================================================")
  data4 = """@prefix A: <http://example.org/A#> .
  @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
  @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
  @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
  
  A:A a rdfs:Class .
  
  <http://example.org/A#instance_0:undefined> xsd:string A:S .
  
  <http://example.org/A#instance_1:p> xsd:string A:S .
  
  A:Aa rdfs:member A:A .
  
  A:Ab rdfs:member A:A .
  
  A:B rdfs:isDefinedBy A:Aa,
          A:Ab .
  
  A:S rdf:value A:B .
  
  """
  g4 = Graph()
  g4.parse(data=data4, format="turtle")

  root = URIRef("http://example.org/A#A")

  triple = (URIRef("http://example.org/A#instance_0:undefined"), RDFSTerms["string"], URIRef("http://example.org/A#S"))

  path, names = find_path_back_triples(g4, triple, root)
  pass
