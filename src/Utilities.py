import os

from graphviz import Digraph

from BricksAndTreeSemantics import RDF_PRIMITIVES
from BricksAndTreeSemantics import RULES

DEBUGG = False

def camelCase(sentence):
  camel = sentence.title().replace(" ","")
  return camel

def classCase(word):
  classCase = word.upper()
  return classCase

def debugging(*info):
  if DEBUGG:
    print("debugging", info)


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


def find_path_back_triples(graph, leave_triple, root):
  """
  Find a path from a primitive, which is a leave to the root.
  It's a straight walk back to the root, as it is a tree, but
  one has to watch out for multiple equal leave values.
  Remedy: take the neighbour along, because he is uniquely named.
  """
  path = [leave_triple]

  now = path[0][2]  # neighbour

  while not now == root:
    triple = (now, None, None)
    for s, p, o in graph.triples(triple):
      t = (s, p, o)
      if t not in path:
        if not p in RDF_PRIMITIVES:
          now = o
          path.append(t)


  return path


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
        "Class"    : {
                "colour"   : "red",
                "shape"    : "rectangle",
                "fillcolor": "red",
                "style"    : "filled",
                },
        "Item"   : {
                "colour"   : "orange",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "Value": {
                "colour"   : "green",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "integer": {
                "colour"   : "blue",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "string": {
                "colour"   : "blue",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "boolean": {
                "colour"   : "blue",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "ROOT"     : {
                "colour"   : "red",
                "shape"    : "rectangle",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "linked"   : {
                "colour"   : "green",
                "shape"    : "rectangle",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "other"    : {
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
    # print(type)
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
    # print("from", From,type, dir)
    # print("to", To, type, dir)
    try:
      colour = EDGE_COLOURS[type]
    except:
      colour = EDGE_COLOURS["other"]
    print("from-to", From, To)
    if dir == -1:
      self.dot.edge(From, To,
                    color=colour,
                    label=type
                    )
    elif dir == 1:
      self.dot.edge(To, From,
                    color=colour,
                    label=type
                    )
    else:
      print(">>>>>>>>>>>>>>>> should not come here")

  def makeMe(self, root):
    self.addNode(root, "Class")
    self.__makeGraph(origin=[root], stack=[])
    # print("nodes ", self.nodes)

    no_nodes = len(self.nodes)
    # Add a standalone annotation (invisible node with label)
    # self.dot.node('note', 'number of nodes %s'%no_nodes, shape='plaintext')

    # with self.dot.subgraph() as s:
    #   s.attr(rank='source')  # Push to the top
    #   s.attr(rank='sink')  # Push to the bottom
    #   s.node('note')  # Ensure it's part of the subgraph

    self.dot.graph_attr["label"] = "Graph of : %s with %s nodes\n"%(self.graph_name, no_nodes)  # Add a title
    self.dot.graph_attr["labelloc"] = "t"  # Position title at the top
    self.dot.graph_attr["fontsize"] = "20"  # Adjust font size of the title
    self.dot.graph_attr["ranksep"] = "1.5"
    print("number of nodes:", no_nodes)

  def __makeGraph(self, origin=[], stack=[]):
    defined_nodes = set()
    for q in self.triples:
      if q not in stack:
        s, p, o, dir = q
        if s != origin:
          type = RULES[p]
          # print("that's an o", o)
          # print("that's an s", s, type)
          if str(s) == "":
            pass
          if o not in defined_nodes:
            self.addNode(o, type)
            defined_nodes.add(o)
          if s not in defined_nodes:
            self.addNode(s, type)
            defined_nodes.add(s)
          self.addEdge(s, o, p, dir)
          stack.append(q)  # (s, p, o))
          self.__makeGraph(origin=s, stack=stack)


if __name__ == "__main__":

  # Example RDF Graph
  from rdflib import Graph, URIRef, Literal
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

  print("============================================================")
  g2 = Graph()
  g2.parse(data=data3, format="turtle")

  root = URIRef("http://example.org/k")
  neighbour = URIRef("http://example.org/k#i")
  leave = Literal("123")

  triple = (neighbour, RDFSTerms["integer"], leave)
  triple_ = (leave, RDFSTerms["integer"], neighbour)

  path = find_path_back_triples(g2, triple_, root)
  for t in path:
    print(t)

