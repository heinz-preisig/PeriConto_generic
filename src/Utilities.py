import os

from graphviz import Digraph

from BricksAndTreeSemantics import RDF_PRIMITIVES
from BricksAndTreeSemantics import RULES

DEBUGG = False


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


def find_path_back(graph, leave, neighbour, root):
  """
  Find a path from a primitive, which is a leave to the root.
  It's a straight walk back to the root, as it is a tree, but
  one has to watch out for multiple equal leave values.
  Remedy: take the neighbour along, because he is uniquely named.
  """
  path = [leave]

  now = neighbour

  while not now == root:
    triple = (now, None, None)
    for s, p, o in graph.triples(triple):
      if not p in RDF_PRIMITIVES:
        now = o
        path.append(now)
    triple = (None, None, now)
    for s, p, o in graph.triples(triple):
      if not p in RDF_PRIMITIVES:
        now = s
        path.append(now)

  return path


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
    # triple = (None, None, now)
    # for s, p, o in graph.triples(triple):
    #   t = (s, p, o)
    #   if t not in path:
    #     if not p in RDF_PRIMITIVES:
    #       now = s
    #       path.append(t)

  return path


class TreePlot:
  """
    Create Digraph plot
  """

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
          "member"   : {
                  "colour"   : "orange",
                  "shape"    : "",
                  "fillcolor": "white",
                  "style"    : "filled",
                  },
          "primitive": {
                  "colour"   : "blue",
                  "shape"    : "rectangle",
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
                  "fillcolor": None,
                  "style"    : None,
                  },
          }
  NODE_SPECS["linked"] = NODE_SPECS["Class"]

  def __init__(self, graph_name, graph_triples, class_names):
    self.classes = class_names
    self.triples = graph_triples
    self.dot = Digraph(graph_name)
    self.dot.graph_attr["rankdir"] = "LR"

  def addNode(self, node, type):
    try:
      specs = self.NODE_SPECS[type]
    except:
      specs = self.NODE_SPECS["other"]

    self.dot.node(node,
                  color=specs["colour"],
                  shape=specs["shape"],
                  fillcolor=specs["fillcolor"],
                  style=specs["style"],
                  )

  def addEdge(self, From, To, type, dir):
    try:
      colour = self.EDGE_COLOURS[type]
    except:
      colour = self.EDGE_COLOURS["other"]
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

  def __makeGraph(self, origin=[], stack=[]):
    for q in self.triples:
      if q not in stack:
        s, p, o, dir = q
        if s != origin:
          type = RULES[p]
          self.addNode(o, type)
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

  data = '''  
  @prefix first: <http://example.org/first> .
  @prefix first_I: <http://example.org/first#> .
  @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
  @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
  @prefix s: <http://example.org/s> .
  @prefix s_I: <http://example.org/s#> .
  @prefix second: <http://example.org/second> .
  @prefix second_I: <http://example.org/second#> .
  @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
  
  first: a rdfs:Class ;
      rdf:value first_I:i .  
  s: a rdfs:Class .  
  second: a rdfs:Class .  
  first_I:irem12 rdfs:member first_I:item1 .  
  first_I:item11 rdf:value first_I:log ;
      rdfs:member first_I:item1 .  
  s_I:hello rdf:value s_I:b ;
      rdfs:member s: .  
  s_I:item1 rdf:value s_I:i ;
      rdfs:member s: .  
  s_I:item2 rdf:value s_I:l ;
      rdfs:member s: .  
  second_I:hello rdfs:member second: .  
  first_I:i xsd:integer "123" .  
  first_I:log xsd:boolean "" .  
  s_I:b xsd:boolean "t" .  
  s_I:i xsd:integer "123" .  
  s_I:l xsd:decimal "12.5" .  
  first_I:item1 rdfs:member first: .
  '''

  data2 = '''  
   @prefix first: <http://example.org/first> .
   @prefix first_I: <http://example.org/first#> .
   @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix s: <http://example.org/s> .
   @prefix s_I: <http://example.org/s#> .
   @prefix second: <http://example.org/second> .
   @prefix second_I: <http://example.org/second#> .
   @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

   first: a rdfs:Class ;
       rdf:value first_I:i .  
   first_I:irem12 rdfs:member first_I:item1 .  
   first_I:item11 rdf:value first_I:log ;
       rdfs:member first_I:item1 .   
   first_I:i xsd:integer "123" .  
   first_I:log xsd:boolean "o" .  
   first_I:item1 rdfs:member first: .
   '''

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

#   data2 = '''  @prefix first: <http://example.org/first> .
# @prefix first_I: <http://example.org/first#> .
# @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# @prefix s: <http://example.org/s> .
# @prefix s_I: <http://example.org/s#> .
# @prefix second: <http://example.org/second> .
# @prefix second_I: <http://example.org/second#> .
# @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
#
# first: a rdfs:Class ;
#     rdf:value first_I:i .
#
# s: a rdfs:Class .
#
# second: a rdfs:Class .
#
# first_I:irem12 rdfs:member first_I:item1 .
#
# first_I:item11 rdf:value first_I:log ;
#     rdfs:member first_I:item1 .
#
# s_I:hello rdf:value s_I:b ;
#     rdfs:member s: .
#
# s_I:item1 rdf:value s_I:i ;
#     rdfs:member s: .
#
# s_I:item2 rdf:value s_I:l ;
#     rdfs:member s: .
#
# second_I:hello rdfs:member second: .
#
# first_I:i xsd:integer "123" .
#
# first_I:log xsd:boolean "o" .
#
# s_I:b xsd:boolean "t" .
#
# s_I:i xsd:integer "123" .
#
# s_I:l xsd:decimal "12.5" .
#
# first_I:item1 rdfs:member first: .
#    '''


  g = Graph()
  g.parse(data=data, format="turtle")


  root = URIRef("http://example.org/first")
  neighbour = URIRef("http://example.org/first#i")
  leave = Literal("123")

  path = find_path_back(g, leave, neighbour, root)
  if path:
    print("Path found:", " -> ".join(str(node) for node in path))
  else:
    print("No path found")

  # print("=========================")
  #
  # triple = (neighbour, RDFSTerms["integer"], leave)
  #
  # path = find_path_back_triples(g, triple, root)
  # for t in path:
  #   print(t)

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