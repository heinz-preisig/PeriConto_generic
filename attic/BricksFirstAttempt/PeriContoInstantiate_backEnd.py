"""
Backend to the construction of a data base for coatings formulations

The data are stored in triple stored in triple stores

rule: notation
an instantiated "node" is <<name>>:<<ID>>

"""
import pprint

import glob
import os
import sys

import copy
import os.path
from rdflib.plugins.stores.memory import Memory

# from rdflib import namespace


root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

DELIMITERS = {
        "instantiated": ":",
        "path"        : "/"
        }
# A temperary URI for our coating ontology
BASE = 'http://example.org/'
ROOT = "ROOT"

from rdflib import Namespace, Literal, URIRef, namespace
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.namespace import RDF, XSD, RDFS

from treeid import ObjectTreeNonUniqueTags, invertDict

# from graphviz import Digraph
import graphviz


ONTOLOGY_REPOSITORY = "../ontologyRepository"

PRIMITIVES = ["string", "integer", "decimal", "boolean", "aniURI"]

RDFSTerms = {
        "Class"      : RDFS.Class,
        "type"       : RDF.type,  # was "is_type"
        "member"     : RDFS.member,
        "isDefinedBy": RDFS.isDefinedBy,
        "value"      : RDF.value,
        "Datatype"   : RDFS.Datatype,
        "comment"    : RDFS.comment,
        "integer"    : XSD.integer,
        "string"     : XSD.string,
        "decimal"    : XSD.decimal,
        "anyURI"     : XSD.anyURI,
        "label"      : RDFS.label,
        "boolean"    : XSD.boolean,
        }

MYTerms = {v: k for k, v in RDFSTerms.items()}  # reverse dictionary

EDGE_COLOUR = {
        "member"     : "blue",
        "isDefinedBy": "red",
        "value"      : "black",
        "comment"    : "green",
        "integer"    : "darkorange",
        "string"     : "cyan",
        }

NODE_COLOUR = {
        "root"        : "red",
        "member"      : "white",
        "sub_class"   : "white",
        "linked_class": "red",
        "isDefinedBy" : "red",
        "primitive"   : "green",
        "value"       : "lightblue",
        "comment"     : "green",
        "integer"     : "green",
        "string"      : "green",
        "instantiated": "yellow",
        "default"     : "white",
        }

NODE_BOUNDARY = {
        "root"        : "red",
        "sub_class"   : "black",
        "linked_class": "red",
        "primitive"   : "green",
        "value"       : "lightblue",
        "comment"     : "green",
        "integer"     : "green",
        "string"      : "green",
        "instantiated": "yellow",
        "default"     : "white",
        }

NODE_SHAPE = {
        "root"        : "ellipse",
        "sub_class"   : "ellipse",
        "linked_class": "egg",
        "primitive"   : "ellipse",
        "value"       : "box",
        "comment"     : "ellipse",
        "integer"     : "box",
        "string"      : "box",
        "instantiated": "box",
        "default"     : "box",
        }


def makeRDFCompatible(identifier):  # TODO remove
  #   """
  #   To be adapted to imported notation.
  #   For now it generates rdflib Literals
  #   """
  return Literal(identifier)


def nodeTypeMembership(node_types, node_tag):
  node_original = getID(node_tag)
  is_root = node_original in node_types["ROOT"]
  is_data_class = node_original in node_types["isDefinedBy"]
  # is_container_class = node in self.node_types[]
  is_sub_class = node_original in node_types["member"]
  is_primitive = node_original in PRIMITIVES
  is_value = node_original in node_types["value"]
  is_comment = node_original in node_types["comment"]
  is_integer = node_original == "integer"
  is_string = node_original == "string"
  # is_linked = node_original in node_types["(predicate == "link_to_class")
  is_instantiated_object = DELIMITERS["instantiated"] in node_tag
  return is_root, \
    is_comment, \
    is_data_class, \
    is_instantiated_object, \
    is_integer, \
    is_primitive, \
    is_string, \
    is_sub_class, \
    is_value


def nodeAttributes(node_types, node_tag, txt_class_names):
  attributes = {
          "color"    : "white",
          "style"    : "filled",
          "fillcolor": "white",
          "shape"    : "none",
          }
  is_root, \
    is_comment, \
    is_data_class, \
    is_instantiated_object, \
    is_integer, \
    is_primitive, \
    is_string, \
    is_sub_class, \
    is_value = nodeTypeMembership(node_types, node_tag)
  if is_root:
    t = "root"
  elif node_tag in txt_class_names:
    t = "linked_class"
  elif is_sub_class:
    t = "sub_class"
  elif is_value:
    t = "value"
  elif is_comment:
    t = "comment"
  elif is_integer:
    t = "integer"
  elif is_string:
    t = "string"
  elif is_instantiated_object:
    t = "instantiated"
  else:
    t = "default"

  attributes["fillcolor"] = NODE_COLOUR[t]
  attributes["shape"] = NODE_SHAPE[t]
  attributes["color"] = NODE_BOUNDARY[t]

  return attributes


def treePlot(objTree, root, node_types, txt_class_names):
  """
  attribute documentation
  https://graphviz.org/doc/info/attrs.html
  """
  dot = graphviz.Digraph(edge_attr={"simplify": "true"})
  # edge_attr = {}
  # edge_attr["tailport"] = "e"
  # edge_attr["headport"] = "w"
  #
  # dot.edge_attr = edge_attr

  edges = set()
  root_str = str(objTree["nodes"][root])
  root_orig = getID(root_str)
  root_str = root_str.replace(":", "-")
  atr = nodeAttributes(node_types, root_orig, txt_class_names)
  # print("debugging ", root_str, atr)
  dot.node(root_str,
           color=atr["color"],
           fillcolor=atr["fillcolor"],
           style=atr["style"],
           shape=atr["shape"]
           )  # str(root))
  # dot.attr("node",**atr)
  for node_ID in objTree["tree"].walkDepthFirst(root):
    children = objTree["tree"].getChildren(node_ID)
    node_str = str(objTree["nodes"][node_ID])
    node_str = node_str.replace(":", "-")
    # if node_str == "A":
    #   print("debugging -- check on A")
    for child in children:
      child_str = str(objTree["nodes"][child])
      child_orig = getID(child_str)
      child_str = child_str.replace(":", "-")
      atr = nodeAttributes(node_types, child_orig, txt_class_names)
      # print("debugging ", child_str, atr)
      dot.node(child_str,
               color=atr["color"],
               fillcolor=atr["fillcolor"],
               style=atr["style"],
               shape=atr["shape"])  # str(child))
      # dot.attr("node",**atr)
      edges.add((child_str, node_str))
      # dot.edge(child_str, node_str) #, arrowhead="none") #str(child), str(node_ID))
    # print("debugg -- children of node %s: %s"%(node_ID, children))
  for (child_str, node_str) in edges:
    dot.edge(child_str, node_str)

  return dot


def plotQuads(graph, class_names=[""]):
  """
  Create Digraph plot
  color names : https://graphviz.org/doc/info/colors.html
  """
  dot = graphviz.Digraph()
  # Add nodes 1 and 2
  suffix = 0
  for s, p, o in graph.triples((None, None, None)):
    ss = str(s)
    ss_ = str(ss).replace(":", "-")
    sp = str(p)
    so = str(o)
    so_ = str(o).replace(":", "-")
    s_ID = getID(str(s))
    if s_ID in PRIMITIVES:  # primitives are not having a unique name so we equip them with an incremental suffix
      if isInstantiated(ss):
        ss_ += "_%s" % suffix
        suffix += 1
    o_ID = getID(str(o))
    if o_ID in PRIMITIVES:
      if isInstantiated(so):
        so_ += "_%s" % suffix
        suffix += 1
    if getID(ss) in class_names:
      dot.node(ss_, color='red', style="filled", fillcolor="lightcoral", shape="none")
    elif getID(so) in PRIMITIVES:
      if isInstantiated(so):
        dot.node(so_, color='green', style='filled', fillcolor="yellow", shape="none")
      else:
        dot.node(so_, color='green', style='filled', fillcolor="gray", shape="none")
    else:
      dot.node(ss_)

    if so == class_names[0]:
      dot.node(so_, style="filled", fillcolor="red", shape="none")
    else:
      dot.node(so_)


    my_p = MYTerms[p]
    dot.edge(ss_, so_,
             # label=my_p,
             color=EDGE_COLOUR[my_p])
    # if DIRECTION[my_p] == 1:
    #   dot.edge(ss_, so_,
    #            # label=my_p,
    #            color=EDGE_COLOUR[my_p])
    # else:
    #   dot.edge(ss_, so_,
    #            # label=my_p,
    #            color=EDGE_COLOUR[my_p])

  return dot


def LegendPlot():
  """
  Create Digraph plot
  """
  dot = graphviz.Digraph()

  atr = {
          "label"   : "Legend",
          "style"   : "solid",
          "rankdir" : "TB",
          "bb"      : "rectangle",
          # "ranksep" : "0.05",
          # "nodesep" : "0.01",
          "labelloc": "b",
          # "len"     : "0",
          "shape"   : "none",
          }

  l = graphviz.Digraph(node_attr=atr, name="Legend")  # {"style": "filled", "shape": 'none', "rankdir":"LR"})

  # l.node("legend", label="Legend", shape="box")
  for i in EDGE_COLOUR:
    s = i + " "
    l.node(s, label=i)
    l.node("o", label="o")
    l.edge(s, "o", color=EDGE_COLOUR[i])

  dot.subgraph(l)
  return dot


def debuggPlotAndRender(graph, file_name, debugg):
  """
  @graph is an RDF graph
  @file_name is to generate a file name
  @debugg  is a convenience variable to help debugging
  """
  if debugg:
    dot = plotQuads(graph)
    dot.render(file_name, view=True)


def debuggTreePlotAndRender(tree, root, node_types, file_name, txt_class_names):
  dot = treePlot(tree, root, node_types, txt_class_names)
  dot.render(file_name, view=True)


def convertRDFintoInternalMultiGraph(graph, graph_ID):
  """
  The quads are not triples, but non-directed graph nodes augmented with predicate an node identifier
  """
  quads = []
  for subject, predicate, object_ in graph.triples((None, None, None)):
    s = str(subject)
    p = MYTerms[predicate]
    o = str(object_)
    if p not in ["value", "isDefinedBy", "Datatype"]:
      quads.append((s, o, p, graph_ID))
    else:
      quads.append((o, s, p, graph_ID))
  # print('debugging.....', quads)
  return quads


def convertQuadsGraphIntoRDFGraph(quads):
  graph = Graph()
  for f, s, p, graphID in quads:
    if p not in ["value", "isDefinedBy"] + PRIMITIVES:
      graph.add((Literal(f), RDFSTerms[p], Literal(s)))
    else:
      graph.add((Literal(s), RDFSTerms[p], Literal(f)))
  print('debugging...printed rdf graph:', graph)
  return graph


def extractClassName(iri):
  return str(iri).split("/")[-1]


def extractItemName(iri):
  if "#" not in str(iri):
    return None
  else:
    _, item = str(iri).split("#")
    return item


def extractSubTree(quads, root, extracts=[], stack=[]):
  for s, o, p, graphID in quads:
    if o == root:
      extracts.append((s, o, p, graphID))
      if o not in stack:
        extractSubTree(quads, s, extracts, stack)


def debuggPrintGraph(graph, debug, text=""):
  if debug:
    print("\ndebugging: %s" % text)
    for s, p, o in graph.triples((None, None, None)):
      print(str(s), MYTerms[p], str(o))


class SuperGraph():
  def __init__(self):
    self.JsonFile = None
    self.ttlFile = None
    self.txt_root_class = ROOT
    self.txt_class_path = []
    self.txt_class_names = set()   #
    self.txt_member_names = {}
    self.txt_is_linked = {}
    self.class_definition_sequence = []
    self.txt_primitives = {}
    self.txt_elucidations = {}
    # self.txt_value_lists = {}
    # self.txt_integer_lists = {}
    # self.txt_string_lists = {}
    self.id_in_graph = {}
    self.txt_comment_lists = {}
    self.enumerators = {}

    self.RDFGraphDictionary = {}

    pass


  def load(self, JsonFile):
    """
    load conjunctive graph from json file and
    """
    self.JsonFile = JsonFile

    # self.project_name = os.path.basename(self.project_file_spec).split(os.path.extsep)[0]

    data = ConjunctiveGraph("Memory")
    data.parse(JsonFile, format="trig")  # FILE_FORMAT)

    self.conjunctiveGraph = data

    # self.txt_class_names = set()
    rdfclasses = set()
    RDFS = namespace.RDFS
    for s, p, o, g in data.quads((None, None, None, None)):
      if o == RDFS.Class:
        print(extractClassName(s))
        self.txt_class_names.add(extractClassName(s))
        rdfclasses.add(s)

    # self.namespaces = {}
    for g in self.txt_class_names:
      # self.namespaces[g] = Namespace(g)
      self.RDFGraphDictionary[g] = Graph()
      self.id_in_graph[g] = set()

    # self.txt_class_names = txt_class_names

    self.txt_root_class = "ROOT"  # data["root"]
    self.txt_elucidations = {}  # data["elucidations"]
    for g in self.txt_class_names:
    #   self.class_definition_sequence.append(g)  # todo: that goes wrong -- used?

      self.txt_member_names[g] = set()
      # self.txt_primitives[g] = {g: []}
      self.txt_is_linked[g] = set()
      self.txt_primitives[g] = {}
      for p in PRIMITIVES:
        self.txt_primitives[g][p] = []
      # self.txt_is_linked[g] = set()

    for s, p, o, g in data.quads((None, None, None, None)):
      if o not in RDFS.Class:
        s_name = extractItemName(s)
        p_name = extractItemName(p)
        o_name = extractItemName(o)
        g_name = extractClassName(g).split(">")[0]
        if not o_name:
          # g_name = extractClassName(g).split(">")[0]
          o_name = g_name.split("/")[-1]
        if p_name == "member":
          self.txt_member_names[g_name].add(s_name)
        elif p_name == "isDefinedBy":
          self.txt_is_linked[g_name].add(s_name)
        elif s_name in PRIMITIVES:
          self.txt_primitives[g_name][s_name].append(o_name)
        self.addGraphGivenInInternalNotation(s_name, p_name, o_name, g_name)



    self.knowledge_tree, self.node_types = self.makeTreeRepresentation()

    self.knowledge_tree["tree"].printMe()
    pass

  def makeTreeRepresentation(self):
    graph_overall = self.collectGraphs()
    mquads = convertRDFintoInternalMultiGraph(graph_overall, "ROOT")  # 'ROOT')
    tree = ObjectTreeNonUniqueTags(self.txt_root_class)
    self.recurseTree(tree, self.txt_root_class, mquads)
    # print("debugging -- generating tree")

    types = {"ROOT": self.txt_root_class}
    for t in list(RDFSTerms.keys() - PRIMITIVES):
      types[t] = set()
    for s, o, p, g in mquads:
      types[p].add(s)

    # print("debugging")
    return tree, types

  def recurseTree(self, tree, id, mquads):

    visited = set()
    stack = [id]
    while stack:
      print(stack)
      id = stack[0]
      stack = stack[1:]
      if id in visited:
        if not stack:
          break
        id = stack[0]
        stack = stack[1:]
      # nodes.append(cur_node)
      children = []
      for s, o, p, g in mquads:
        if o == id:
          children.append(str(s))
      for child in reversed(children):  # .get_rev_children():
        tree.addChildtoNode(child, id)
        if id not in self.txt_class_names:
          self.id_in_graph[g].add(id)
        else:
          if id not in self.class_definition_sequence:
            self.class_definition_sequence.append(id)
        if child not in stack:
          stack.insert(0, child)
      pass
      visited.add(id)

  def collectGraphs(self):
    graph_overall = Graph()
    for cl in self.RDFGraphDictionary:
      # print('debugging.....', cl)
      for t in self.RDFGraphDictionary[cl].triples((None, None, None)):
        # print('debugging...', t)
        s, p, o = t
        graph_overall.add(t)
    return graph_overall

  def makeURI(self, Class, identifier):
    uri = URIRef(self.namespaces[Class] + "#" + identifier)
    # print("uri: ", identifier, "-->", uri)
    return uri

  def makeClassURI(self, Class):
    uid = "%s/%s" % (BASE, Class)
    uris = URIRef(uid)
    return uid, uris

  def addGraphGivenInInternalNotation(self, subject_internal, predicate_internal, object_internal, graph_ID):
    rdf_subject = makeRDFCompatible(subject_internal)
    rdf_object = makeRDFCompatible(object_internal)
    rdf_predicate = RDFSTerms[predicate_internal]
    self.RDFGraphDictionary[graph_ID].add((rdf_subject, rdf_predicate, rdf_object))

  def printMe(self, text):

    for g in list(self.RDFGraphDictionary.keys()):
      print("\n %s %s" % (text, g))
      for s, p, o in self.RDFGraphDictionary[g].triples((None, None, None)):
        print("- ", str(s), MYTerms[p], str(o))

  def to_rdflibConjunctiveGraph(self):

    # Define a namespace for our coating knowledge graph and link the URI
    ckg = Namespace(BASE)
    print("....debugging...", ckg)
    kg_store = Memory()
    kg = ConjunctiveGraph(store=kg_store)  # kg_store)
    kg.bind("ckg", ckg)

    for subgraph_key in list(self.RDFGraphDictionary.keys()):

      # print("printing the subgraph identifier....", subgraph_key)
      print(".....URI of subgraph", ckg[subgraph_key])
      print("=================================")
      subgraph = Graph(identifier=subgraph_key, store=kg_store)  # store=kg_store, identifier=subgraph_key)
      for s, p, o in self.RDFGraphDictionary[subgraph_key].triples((None, None, None)):
        subgraph.add((ckg[s], p, ckg[o]))
        # print(p)
        print(ckg[s], p, ckg[o])
        # subgraph.add(ckg[s], RDFSTerms[p], ckg[o])

    # print conjunctive graph contexts
    print("Graph Contexts:")
    for c in kg.contexts():
      print(f"-- {c.identifier} ")

    return kg

  # def rdfSerializer(self, format):
  #   return self.RDFGraphDictionary.serialize(format)


# def makeListBasedOnPredicates(rdf_graph, rdf_predicate):
#   subclasslist = []
#   for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
#     subclasslist.append(str(s))  # (str(s), txt_class, str(o)))
#   return subclasslist


# def makeLinkListBasedOnPredicates(rdf_graph, txt_class, rdf_predicate):
#   subclasslist = []
#   for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
#     subclasslist.append((str(s), txt_class, str(o)))
#   return subclasslist


class ContainerGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    self.enumerators = {}  # {"classes"         : {},
    # "nodes_in_classes": {}}
    pass

  def loadData(self, JsonFile):
    # super().load(JsonFile)
    self.load(JsonFile)
    for class_ID in self.RDFGraphDictionary:

      # self.enumerators["classes"][class_ID] = -1
      # self.enumerators["nodes_in_classes"][class_ID] = {}
      for s, p, o in self.RDFGraphDictionary[class_ID]:
        self.enumerators[str(s)] = -1
        self.enumerators[str(o)] = -1
      #   self.enumerators["nodes_in_classes"][class_ID][str(o)] = -1  # instantiate enumerators
      #   self.enumerators["nodes_in_classes"][class_ID][str(s)] = -1  # instantiate enumerators
    for p in PRIMITIVES:
      self.enumerators[p] = -1

    return self.txt_root_class

  def incrementClassEnumberator(self, class_ID):
    v = self.enumerators["classes"][class_ID]
    v += 1
    self.enumerators["classes"][class_ID] = v
    return v

  def incrementNodeEnumerator(self, class_ID, node_ID):
    v = self.enumerators["nodes_in_classes"][class_ID][node_ID]
    v += 1
    self.enumerators["nodes_in_classes"][class_ID][node_ID] = v
    return v

  def incrementPrimitiveEnumerator(self, primitive):
    v = self.enumerators[primitive]
    v += 1
    self.enumerators[primitive] = v
    return v


class DataGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass


class Data(dict):
  def __init__(self):
    dict.__init__(self)
    self.enum = 0
    self.integers = {}
    self.strings = {}

  def addInteger(self, path, IDs, value):
    path_enum = self.addPath(path)
    key = (path_enum, IDs)
    print("debugging -- integer add key", key, value)
    if key not in self.integers:
      self.integers[key] = value
    else:
      print("adding integer >>> error")

  def addString(self, path, IDs, string):  # addString(global_path, global_IDs, value)
    path_enum = self.addPath(path)
    key = (path_enum, IDs)
    # print("debugging -- string add key", key, string)
    if key not in self.strings:
      self.strings[key] = string
    else:
      print("adding string >>> error")

  def addPath(self, path):
    for p in self.values():
      if p == path:
        enum = self.getEnumerator(path)
        # print("Data: path already exists", enum, p)
        return enum

    self.enum += 1
    self[self.enum] = path
    return self.enum

  def getPath(self, enum):
    if enum in self:
      return self[enum]
    else:
      return None

  def getEnumerator(self, path):
    for enum in self:
      if self[enum] == path:
        return enum

    return None


class WorkingTree(SuperGraph):

  def __init__(self, container_graph):
    SuperGraph.__init__(self)
    debugg = False
    self.container_graph = container_graph
    self.data = Data()
    self.tree = copy.deepcopy(container_graph.knowledge_tree)

    node_types = self.container_graph.node_types
    if debugg:
      debuggTreePlotAndRender(self.tree, 0, node_types, "base_ontology", self.txt_class_names)

  def instantiateAlongPath(self, paths_in_classes, class_path):

    debug = True

    print("debugging -- class path and paths in classes", class_path, paths_in_classes)

    instantiated = {}

    # we start at the end, where the primitive was just instantiated
    c = class_path[-1]
    c_original = getID(c)
    from_graph = copy.deepcopy(self.RDFGraphDictionary[c])

    debuggPrintGraph(from_graph, debug, text="starting")
    # print("debugging -- >>>>>>>>>>>> ", class_path, c)
    nodes = paths_in_classes[c].split(DELIMITERS["path"])

    instantiated[c_original] = {}  # keep track on what node in the path has been instantiated

    primitive = nodes[-1]  # get the primitive
    primitive_name = nodes[-2]  # that's the node with the name for the primitive
    value_name = nodes[-3]  # that's the quantity given a value with the name being the node [-2]

    if primitive not in PRIMITIVES:
      print("error >>>>>>>  %s must be a primitive" % primitive)
      return

    # both must not be instantiated
    if isInstantiated(primitive) or isInstantiated(primitive_name) or isInstantiated(value_name):
      print("error >>>>>>>>  neither node can be instantiated", primitive, primitive_name, value_name)
      return

    primitive_enum = self.container_graph.incrementPrimitiveEnumerator(getID(primitive))
    primitive_i = makeID(primitive, primitive_enum)
    instantiated[c_original][primitive] = primitive_i

    primitive_name_enum = self.container_graph.incrementNodeEnumerator(c_original, getID(primitive_name))
    primitive_name_i = makeID(primitive_name, primitive_name_enum)
    instantiated[c_original][primitive_name] = primitive_name_i

    value_name_enum = self.container_graph.incrementNodeEnumerator(c_original, getID(value_name))
    value_name_i = makeID(value_name, value_name_enum)
    instantiated[c_original][value_name] = value_name_i

    from_graph.remove((Literal(primitive_name), RDFSTerms[primitive], Literal(primitive)))
    from_graph.add((Literal(primitive_name_i), RDFSTerms[primitive], Literal(primitive_i)))

    from_graph.remove((Literal(value_name), RDFSTerms["value"], Literal(primitive_name)))
    from_graph.add((Literal(value_name_i), RDFSTerms["value"], Literal(primitive_name_i)))

    node_list = reversed(nodes[1:-2])
    stop = False
    for n in node_list:
      for s, p, o in from_graph.triples((Literal(getID(n)), RDFSTerms["is_a_subclass_of"], None)):
        n_i = instantiated[c_original][n]
        if isInstantiated((str(o))):  # hit an instantiated node
          from_graph.remove((s, p, o))
          from_graph.add((Literal(n_i), p, o))
          # print("debugging - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> stop 1")
          stop = True
          debuggPrintGraph(from_graph, debug, text="stop 1")
          break
        else:
          o_original = getID(str(o))
          o_enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
          o_i = makeID(o_original, o_enum)
          instantiated[c_original][o_original] = o_i
          from_graph.remove((s, p, o))
          from_graph.add((Literal(n_i), p, Literal(o_i)))

    # debuggPrintGraph(from_graph, debug, text="completed node list")

    for n in instantiated[c_original]:
      n_i = instantiated[c_original][n]
      for s, p, o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], Literal(n))):
        from_graph.remove((s, p, o))
        from_graph.add((s, p, Literal(n_i)))

    # debuggPrintGraph(from_graph, debug)

    if c in instantiated[c_original]:
      c_store = instantiated[c_original][c]
      # del self.RDFConjunctiveGraph[c]  # todo: here it is deleted
      self.RDFGraphDictionary[c_store] = from_graph
      # print("debugging -- put the graph into to conjunctive graph")
      index = class_path.index(c)
      class_path[index] = c_store
    else:
      c_store = c

    if not isInstantiated(c):
      c_i = instantiated[c][c]
    else:
      c_i = c

    t = self.updatePathsInClasses(c, instantiated, paths_in_classes)
    del paths_in_classes[c]
    paths_in_classes[c_i] = t

    if stop:
      self.RDFGraphDictionary[c_store] = from_graph
      return class_path, paths_in_classes

    ### end of the first class, the class where the instantiation took place, being modified

    for c in reversed(class_path[:-1]):
      linked_node = nodes[0]  # this is the link to the previous class

      # linked_node_i = instantiated[c_original][linked_node]
      c_previous_original = c_original

      c_original = getID(c)
      # print("debugging -- >>>>>>>>>>>> ", class_path, c)
      nodes = paths_in_classes[c].split(DELIMITERS["path"])
      linked_to_node = nodes[-2]
      from_graph = copy.deepcopy(self.RDFGraphDictionary[c])

      debuggPrintGraph(from_graph, debug, text="before handling the links")

      instantiated[c_original] = {}  # OrderedDict()  # here it is set
      for s, p, o in from_graph.triples((Literal(linked_node), RDFSTerms["link_to_class"], Literal(linked_to_node))):
        from_graph.remove((s, p, o))
        o_enum = self.container_graph.incrementNodeEnumerator(c_original, str(o))
        o_i = makeID(str(o), o_enum)
        instantiated[c_original][str(o)] = o_i
        s_i = instantiated[c_previous_original][str(s)]
        from_graph.add((Literal(s_i), p, Literal(o_i)))

      debuggPrintGraph(from_graph, debug, text="after handling the links")

      node_list = reversed(nodes[0:-1])
      for n in node_list:

        for s, p, o in from_graph.triples((n, RDFSTerms["is_a_subclass_of"], None)):
          if n in instantiated[c_original]:
            n_i = instantiated[c_original][n]
          else:
            n_enum = self.container_graph.incrementNodeEnumerator(c_original, getID(n))
            n_i = makeID(n, n_enum)
          if isInstantiated((str(o))):  # hit an instantiated node
            from_graph.remove((s, p, o))
            from_graph.add((Literal(n_i), p, o))
            # print("debugging - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> stop 2")
            stop = True
            break
          else:
            o_original = getID(str(o))
            o_enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
            o_i = makeID(o_original, o_enum)
            instantiated[c_original][o_original] = o_i
            from_graph.remove((s, p, o))
            from_graph.add((Literal(n_i), p, Literal(o_i)))

      # debuggPrintGraph(from_graph, debug)

      for n in instantiated[c_original]:
        n_i = instantiated[c_original][n]
        for s, p, o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], Literal(n))):
          from_graph.remove((s, p, o))
          from_graph.add((s, p, Literal(n_i)))

      debuggPrintGraph(from_graph, debug, text="putting things back")

      c_store = c
      if c in instantiated:
        node_no = self.container_graph.incrementClassEnumberator(c)
        c_i = makeID(c, node_no)
        index = class_path.index(c)
        class_path[index] = c_i
        c_store = c_i
        instantiated[c][c] = c_i
        # del instantiated[c]
        del self.RDFGraphDictionary[c]

      self.RDFGraphDictionary[c_store] = from_graph

      if not isInstantiated(c):
        c_i = instantiated[c][c]
      else:
        c_i = c
      t = self.updatePathsInClasses(c, instantiated, paths_in_classes)
      del paths_in_classes[c]
      paths_in_classes[c_i] = t
      if stop:
        return class_path, paths_in_classes

    return class_path, paths_in_classes

  def updatePathsInClasses(self, c, instantiated, paths_in_classes):
    c_original = getID(c)
    nodes = paths_in_classes[c].split(DELIMITERS["path"])
    new_nodes = []
    for n in nodes:
      if n in instantiated[c_original]:
        new_nodes.append(instantiated[c_original][n])
      else:
        # print(">>>>>>>>>>>troubles", c, c_original, n)
        new_nodes.append(n)
    t = DELIMITERS["path"].join(new_nodes)
    return t

  def makeRDFDotGraph(self):
    graph_overall = self.collectGraphs()
    class_names = list(self.RDFGraphDictionary.keys())
    dot = plotQuads(graph_overall, class_names)
    graph_name = self.txt_root_class
    dot.render(graph_name, directory=ONTOLOGY_REPOSITORY, view=True)
    if not os.path.exists(os.path.join(ONTOLOGY_REPOSITORY, "legend.pdf")):
      # TODO: add button for legend
      leg = LegendPlot()
      leg.render("legend", directory=ONTOLOGY_REPOSITORY, view=True)
    return dot

  def collectGraphs(self):
    graph_overall = Graph()
    for cl in self.RDFGraphDictionary:
      for t in self.RDFGraphDictionary[cl].triples((None, None, None)):
        s, p, o = t
        graph_overall.add(t)
    # class_names = list(self.RDFConjunctiveGraph.keys())
    # dot = plot(graph_overall, class_names)
    # graph_name = self.txt_root_class
    return graph_overall

  def extractSubgraph(self, root, graph_ID):
    """
    extract an RDF-subgraph from an RDF-Graph given a root as a string, a label
    it is done via the quads generation that ignore the directionality
    """
    mquads = convertRDFintoInternalMultiGraph(self.container_graph.RDFGraphDictionary[graph_ID], graph_ID)
    extracts = []  # TODO: add button for legend
    extractSubTree(mquads, root, extracts)  # as quads
    graph = convertQuadsGraphIntoRDFGraph(extracts)
    linked_classes = []
    debuggPlotAndRender(graph, "adding", True)
    c_next = None
    for s, p, o in graph.triples((None, RDFSTerms["link_to_class"], None)):
      c_next = getID(str(s))
      if c_next:
        linked_classes.append(c_next)
        self.getLinkedGraphs(c_next, linked_classes, stack=[])

    return graph, linked_classes

  def getLinkedGraphs(self, c_current, linked_classes, stack=[]):
    graph = self.container_graph.RDFGraphDictionary[c_current]
    stack.append(c_current)
    for s, p, o in graph.triples((None, RDFSTerms["link_to_class"], None)):
      c_next = getID(str(s))
      if c_next not in stack:
        linked_classes.append(c_next)
        stack.append(c_next)
        self.getLinkedGraphs(c_next, linked_classes, stack=stack)


def isInstantiated(ID):
  id = str(ID)
  # print("debugging ==", id,(DELIMITERS["instantiated"] in id))
  return DELIMITERS["instantiated"] in id


def getID(ID):
  if DELIMITERS["instantiated"] in ID:
    container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  else:
    container_graph_ID = ID
  return container_graph_ID


def getIDNo(ID):
  if DELIMITERS["instantiated"] in ID:
    container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  else:
    instance_ID = None
  return instance_ID


def makeID(ID, no):
  return ID + DELIMITERS["instantiated"] + str(no)


class Enumerator(int):
  def __init__(self):
    self = 0

  def newValue(self):
    self += 1
    return self


class Stack(dict):
  def __init__(self):
    dict.__init__(self)

  def push(self, key, item):
    self[key] = item

  def pop(self, key):
    v = self[key]
    return v

  def reduce(self, keys):
    delete_key = []
    for k in self:
      if k not in keys:
        delete_key.append(k)
    for k in delete_key:
      del self[k]


class BackEnd:

  def __init__(self, FrontEnd):

    global state

    self.FrontEnd = FrontEnd
    self.changed = False

    self.ContainerGraph = ContainerGraph()
    # data_container = {}
    self.working_tree = None

    self.ui_state("start")
    self.current_node = None
    self.current_class = None
    self.current_subclass = None
    self.data_container_number = 0
    self.class_path = []

    self.path_at_transition = Stack()  # Note: path at the point of transition to another class. Key: class_ID

    self.instanceEnumerator = Enumerator()

    self.automaton = self.automaton()

  def __askForFileNameOpening(self):
    global current_event_data
    global automaton_next_state

    state = automaton_next_state

    self.FrontEnd.fileNameDialogOpen(state, "file_name",
                                     "ontology",
                                     ONTOLOGY_REPOSITORY,
                                     "*",
                                     "exit")

  def __askForFileNameKnowledgeGraphLoading(self):
    global current_event_data
    global automaton_next_state

    state = automaton_next_state

    self.FrontEnd.fileNameDialogOpen(state, "file_name",
                                     "instantiate knowledge graph",
                                     ONTOLOGY_REPOSITORY,
                                     "*",
                                     "exit")

  def __askForFileNameSaving(self):
    global current_event_data
    global automaton_next_state

    state = automaton_next_state

    self.FrontEnd.fileNameDialogSave(state, "file_name",
                                     "ontology",
                                     ONTOLOGY_REPOSITORY,
                                     "*.ttl",
                                     "exit")

  def __saveKnowledgeGraph(self):
    """Saving knowledge graph or the loaded ontology in the turtle format.
    It allows currently to save turtle serialized version  of the loaded ontology.
    #TODO: save the instantiated knowledge graph.
    """
    # self.current_kg = self.ContainerGraph.to_rdflibConjunctiveGraph()
    # self.current_kg_turtle = self.currentkg.rdfSerializer('turtle')

    # write current_kg_turtle data to a file
    global current_event_data
    filename_save = current_event_data["file_name"]

    self.ttlFile = os.path.join(ONTOLOGY_REPOSITORY, filename_save)
    print('printing filepath to save ttl..', self.ttlFile)
    current_kg = self.ContainerGraph.to_rdflibConjunctiveGraph()

    print("turtle serialised KG...", current_kg.serialize(format='nquads'))
    # oops--- ttl format data written to the file is not in a newline format!
    # saveWithBackup dumps only json data, so it won't work here.
    # TODO: change putData method in PeriConto.py to enable ttl format

    # saveWithBackup(current_kg.serialize(format='turtle'), self.ttlFile)

    # a temporary fix
    current_kg.serialize(format='nquads', destination=filename_save)

  def __askToQuit(self):
    pass

  def __loadOntology(self):
    global current_event_data

    file_name = current_event_data["file_name"]

    event_data = current_event_data
    self.root_class_container = self.ContainerGraph.loadData(file_name)

    self.ContainerGraph.printMe("loaded")

    self.working_tree = WorkingTree(self.ContainerGraph)
    self.txt_class_names = list(self.working_tree.container_graph.RDFGraphDictionary.keys())

    self.current_class = self.root_class_container

  def __loadKnowledgeGraph(self):
    global current_event_data
    global automaton_next_state

    file_name = current_event_data["file_name"]  # "new.ttl"
    data = open(file_name)
    g = ConjunctiveGraph()
    g.parse(data, format="trig")

    self.__askForFileNameOpening()
    self.__loadOntology()

    kg = self.ContainerGraph.conjunctiveGraph


    g_kg = g + kg
    pass
    self.ContainerGraph.conjunctiveGraph = g_kg
    self.working_tree = WorkingTree(self.ContainerGraph)
    # self.txt_class_names = list(self.txt_class_names) #working_tree.container_graph.RDFConjunctiveGraph.keys())
    #
    # self.current_class = self.root_class_container

    print("debugging __loadKnowledgeGraph")

  def __processSelectedItem(self):
    #   """
    #   data is a list with selected item ID, associated predicate and a graph ID
    #   """
    global current_event_data
    global automaton_next_state

    reversed_path = current_event_data["reversed_path"]
    node_tag = current_event_data["node_tag"]
    node_ID = current_event_data["node_ID"]

    node_original = getID(node_tag)

    graph = None
    for id in reversed_path:
      node = self.ContainerGraph.knowledge_tree["nodes"][id]
      if node in self.txt_class_names:
        graph = node
        break


    if node_tag in PRIMITIVES:
      if not DELIMITERS["instantiated"] in node_tag:
        if node_tag == "string":
          self.ui_state("instantiate_string")
        elif node_tag == "integer":
          self.ui_state("instantiate_integer")
        elif node_tag == "decimal":
          self.ui_state("instantiate_integer")
        elif node_tag == "boolean":
          self.ui_state("instantiate_boolean")
        elif node_tag == "anyURI":
          self.ui_state("instantiate_string")
        else:
          self.ui_state("show_tree")
        return

    # types = self.working_tree.container_graph.node_types
    instantiated = DELIMITERS["instantiated"] in node_tag
    if instantiated:
      test_tag,_ = node_tag.split(DELIMITERS["instantiated"])
      if (test_tag in self.ContainerGraph.txt_is_linked[graph]):

        # exctract from the working tree to check if one can add a branch
        parent_ID = self.working_tree.tree["tree"].getImmediateParent(node_ID)
        sub_tree, map = self.working_tree.tree["tree"].extractSubTreeAndMap(parent_ID)
        nodes = {}
        for m in map:
          nodes[map[m]] = self.working_tree.tree["nodes"][m]

        print("debugging")
        # if node_original in self.working_tree.tree["nodes"].values(): # too restrictive
        if node_original in nodes.values():  # relaxed constraint
          return
        dialog = self.FrontEnd.dialogYesNo(message="add new ")
        if dialog == "YES":
          self.__addBranch(node_ID)
        elif dialog == "NO":
          pass


  def __addBranch(self, node_ID):
    """
    This is the difficult part.
    Once an instantiated subtree is selected, the respective branch is copied and added to the same parent node.
    """
    debug_plot = False
    debug_print = False

    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    node_tag = current_event_data["node_tag"]
    node_ID = current_event_data["node_ID"]

    node_original = getID(node_tag)
    node_ID_original = self.working_tree.container_graph.knowledge_tree["IDs"][node_original]

    if debug_plot:
      dot = self.working_tree.tree["tree"].plotMe(0)
      dot.render("before", view=True)

    map_before = self.working_tree.tree["tree"].mapMe()
    sub_tree, map = self.working_tree.container_graph.knowledge_tree["tree"].extractSubTreeAndMap(node_ID_original)

    nodes = {}
    for m in map:
      nodes[map[m]] = self.working_tree.container_graph.knowledge_tree["nodes"][m]

    parent_ID = self.working_tree.tree["tree"].getImmediateParent(node_ID)
    adding_map = self.working_tree.tree["tree"].addTree(sub_tree, parent_ID)

    extended_tree_map = self.working_tree.tree["tree"].mapMe()

    inv_map_before = invertDict(map_before)
    inv_adding_map = invertDict(adding_map)

    nodes_extended_tree = {}
    for m in inv_adding_map:
      n = extended_tree_map[m]
      nodes_extended_tree[n] = nodes[inv_adding_map[m]]

    for m in inv_map_before:
      n = extended_tree_map[m]
      nodes_extended_tree[n] = self.working_tree.tree["nodes"][inv_map_before[m]]

    self.working_tree.tree["nodes"] = nodes_extended_tree
    self.working_tree.tree["IDs"] = invertDict(nodes_extended_tree)

    if debug_plot:
      node_types = self.working_tree.container_graph.node_types
      dot = self.working_tree.tree["tree"].plotMe(0)
      dot.render("after", view=True)
      dot = treePlot(self.working_tree.tree, 0, node_types, self.txt_class_names)
      dot.render("after all", view=True)

    self.__showTree()

  def __gotInteger(self):
    global current_event_data
    global automaton_next_state

    value = current_event_data["integer"]
    global_IDs, global_path = self.__addPrimitive()

    self.working_tree.data.addInteger(global_path, global_IDs, value)

    self.ui_state("show_tree")
    self.__showTree()

  def __addPrimitive(self):
    global current_event_data
    reversed_path = current_event_data["reversed_path"]
    node_tag = current_event_data["node_tag"]
    node_ID = current_event_data["node_ID"]
    global_path_list = []
    global_IDs_list = []
    for ID in reversed_path:
      tag = self.working_tree.tree["nodes"][ID]
      if not isInstantiated(tag):
        enum = self.ContainerGraph.incrementPrimitiveEnumerator(getID(tag))
        tag_i = makeID(tag, enum)
        global_IDs_list.append(str(enum))
        self.working_tree.tree.rename(ID, tag_i)
        global_path_list.append(tag)
      else:
        global_path_list.append(getID(tag))
        enum = getIDNo(tag)
        global_IDs_list.append(enum)
    global_path_list.reverse()
    global_IDs_list.reverse()
    enum = self.ContainerGraph.incrementPrimitiveEnumerator(node_tag)
    tag_i = makeID(node_tag, enum)
    global_IDs_list.append(str(enum))
    self.working_tree.tree.rename(node_ID, tag_i)
    global_path_list.append(node_tag)
    # global_IDs_list = []
    # for i in global_path_list:
    #   id = getIDNo(i)
    #   global_IDs_list.append(id)
    global_path = DELIMITERS["path"].join(global_path_list)
    global_IDs = DELIMITERS["instantiated"].join(global_IDs_list)
    return global_IDs, global_path

  def __gotString(self):

    global current_event_data
    global automaton_next_state

    value = current_event_data["string"]
    global_IDs, global_path = self.__addPrimitive()

    self.working_tree.data.addInteger(global_path, global_IDs, value)

    self.ui_state("show_tree")
    self.__showTree()

  def __clearInteger(self):
    self.FrontEnd.controls("selectors", "integer", "populate", {"value": 0})

  def __clearString(self):
    self.FrontEnd.controls("selectors", "string", "clear", )

  def __makeDotPlot(self):

    node_types = self.working_tree.container_graph.node_types
    dot = treePlot(self.working_tree.tree, 0, node_types, self.txt_class_names)
    dot.render("periconto_instantiated", view=True)

  def __updateTree(self):
    global current_event_data
    global automaton_next_state
    # print(">>>", current_event_data, automaton_next_state)

  def __showTree(self):
    self.FrontEnd.controls("selectors", "classTree", "populate", self.working_tree.tree)

  def __shiftClass(self):
    global current_event_data

    if "path" in current_event_data:
      t = current_event_data["path"].split(DELIMITERS["path"])[:-1]
      if len(t) > 0:
        transition_path = "/".join(t) + DELIMITERS["path"]
        previous_class = self.class_path[-1:][0]
        self.path_at_transition.push(previous_class, transition_path)

    class_ID = self.current_class
    if class_ID not in self.class_path:
      self.class_path.append(class_ID)
    else:
      i = self.class_path.index(class_ID)
      self.class_path = self.class_path[:i + 1]
    pass

    self.path_at_transition.reduce(self.class_path[:-1])
    # print("debugging -- transition -- ", self.path_at_transition)

    self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class)
    self.FrontEnd.controls("selectors", "classList", "populate", self.class_path)

    # print(">>>", current_event_data, automaton_next_state)

  def __makeFirstDataRoot(self, container_root_class, data_ID):

    root_class = container_root_class + DELIMITERS["instantiated"] + str(data_ID)
    return root_class

  def processEvent(self, state, Event, event_data):
    # Note: cannot be called from within backend -- generates new name space
    global gui_state
    global current_event_data
    global automaton_next_state
    global action
    # global data_container

    show_automaton = False

    current_event_data = event_data
    print(">>>>>>>>>>>>>>>>>>>>", state, Event, event_data)

    if state not in self.automaton:
      print("stopping here - no such state", state)
      return
    if Event not in self.automaton[state]:
      print("stopping here - no such event", Event, "  at state", state)
      return

    next_state = self.automaton[state][Event]["next_state"]
    actions = self.automaton[state][Event]["actions"]
    gui_state = self.automaton[state][Event]["gui_state"]

    automaton_next_state = next_state

    if show_automaton:
      print("automaton -- ",
            "\n             state   :", state,
            "\n             next    :", next_state,
            "\n             actions :", actions,
            "\n             gui     :", gui_state,
            "\n             data    :", event_data,
            "\n")

    for action in actions:
      action()
      # if action:
      #   action()
    self.ui_state(gui_state)

    return next_state

  def automaton(self):
    automaton = {
            "start"                 : {
                    "initialise": {
                            "next_state": "initialised",
                            "actions"   : [None],
                            "gui_state" : "start"
                            },
                    },
            "load"                  : {
                    "load": {
                            "next_state": "show_tree",
                            "actions"   : [self.__askForFileNameKnowledgeGraphLoading,
                                           self.__loadKnowledgeGraph,
                                           self.__showTree, ],
                            "gui_state" : "show_tree"
                            }
                    },

            "initialised"           : {
                    "create": {
                            "next_state": "got_ontology_file_name",
                            "actions"   : [self.__askForFileNameOpening],
                            "gui_state" : "initialise"
                            },
                    },
            "got_ontology_file_name": {
                    "file_name": {
                            "next_state": "show_tree",
                            "actions"   : [self.__loadOntology,
                                           self.__showTree,
                                           ],
                            "gui_state" : "show_tree"
                            },
                    },
            "show_tree"             : {
                    "selected": {
                            "next_state": "check_selection",
                            "actions"   : [self.__processSelectedItem,
                                           self.__clearInteger,
                                           self.__clearString,
                                           ],
                            "gui_state" : "NoSet"
                            },
                    },
            "wait_for_ID"           : {
                    "got_integer": {
                            "next_state": "show_tree",
                            "actions"   : [self.__gotInteger],
                            "gui_state" : "show_tree"
                            },
                    "got_string" : {
                            "next_state": "show_tree",
                            "actions"   : [self.__gotString],
                            "gui_state" : "show_tree"
                            },
                    },
            "visualise"             : {
                    "dot_plot": {
                            "next_state": "show_tree",
                            "actions"   : [self.__makeDotPlot],
                            "gui_state" : "show_tree"
                            }
                    },
            # Automaton state transition logic to save a loaded ontology or Knowledge Graph
            "save_knowledgeGraph"   : {
                    "save": {
                            "next_state": "do_saving_knowledgeGraph",
                            "actions"   : [self.__askForFileNameSaving],
                            "gui_state" : "show_tree"
                            }
                    },
            "do_saving_knowledgeGraph": {
                    "file_name": {
                            "next_state": "show_tree",
                            "actions"   : [self.__saveKnowledgeGraph],
                            "gui_state" : "show_tree"
                            }
                    },

            # "save_knowledgeGraph"   : {"file_name": {"next_state": "save",
            #                                                "actions"   : [self.__askForFileNameSaving,
            #                                                               self.__saveKnowledgeGraph,
            #                                                               self.__askToQuit],
            #                                                "gui_state" : "quit"}
            #                         },

            # "state"      : {"event": {"next_state": add next state,
            #                                                "actions"   : [list of actions],
            #                                                "gui_state" : specify gui shows (separate dictionary}
            #                          },
            }

    return automaton

  def ui_state(self, state):
    # what to show and clear
    clear = {}
    if state == "start":
      show = {
              "buttons": ["load",
                          "create",
                          "exit",
                          ],
              }
    elif state == "NoSet":
      return

    elif state == "initialise":
      show = {
              "buttons"  : ["load",
                            "create",
                            "exit",
                            ],
              "selectors": ["classList",
                            "classTree"]
              }
    elif state == "show_tree":
      show = {
              "buttons"  : ["save",
                            "exit",
                            "visualise",
                            ],
              "selectors": ["classList",
                            "classTree"],
              }
    elif state == "instantiate_integer":
      show = {
              "buttons"  : ["acceptInteger",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "integer"],
              "groups"   : "integer"
              }
    elif state == "instantiate_string":
      show = {
              "buttons"  : ["acceptString",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "string"],
              "groups"   : ["string"]
              }
    elif state == "selected_subclass":
      show = {
              "buttons" : ["save",
                           "exit", ],
              "textEdit": ["ClassSubclassElucidation",
                           ]
              }
    elif state == "selected_class":
      show = {
              "buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation", "PrimitiveString"],
              }
    elif state == "selected_integer":
      show = {
              "buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation",
                      "integer",
                      ]
              }
    elif state == "selected_string":
      show = {
              "buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation",
                      "PrimitiveString",
                      ]
              }

    elif state == "save_knowledgeGraph":
      show = {
              "buttons": ["save",
                          "exit", ]
              }
    elif state == "quit":
      show = {
              "buttons": ["exit", ]
              }

    else:
      show = []
      print("ooops -- no such gui state", state)

    # print("debugging -- state & show", state, show)

    objs = self.FrontEnd.gui_objects
    obj_classes = list(objs.keys())
    for oc in obj_classes:
      o_list = list(objs[oc].keys())
      for o in o_list:
        self.FrontEnd.controls(oc, o, "hide")
      for o in o_list:
        if oc in show:
          if o in show[oc]:
            self.FrontEnd.controls(oc, o, "show")


if __name__ == "__main__":
  quads = [('c_number', 'c', 'value', 'a'), ('integer', 'c_number', 'integer', 'a'),
           ('c', 'a', 'is_a_subclass_of', 'a'), ('b', 'a', 'is_a_subclass_of', 'a'),
           ('d', 'b', 'is_a_subclass_of', 'a'), ('A', 'd', 'link_to_class', 'a')]
  extracts = []
  extractSubTree(quads, 'b', extracts)
  print(extracts)
