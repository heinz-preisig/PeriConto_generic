import copy
import os

import rdflib
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from BricksAndTreeSemantics import FILE_FORMAT
from BricksAndTreeSemantics import MYTerms
from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import RDFSTerms
from BricksAndTreeSemantics import RDF_PRIMITIVES
from BricksAndTreeSemantics import extractNameFromIRI
from BricksAndTreeSemantics import makeBrickNameSpace
from BricksAndTreeSemantics import makeClassURI
from BricksAndTreeSemantics import makeItemURI
from Utilities import debugging
from Utilities import find_path_back_triples
from Utilities import saveBackupFile

DEBUGG = True


class DataModel:
  def __init__(self, root):
    self.namespaces = {}

    self.BRICK_GRAPHS = {}
    self.TREE_GRAPHS = {}
    self.file_name_bricks = self.makeFileName(root, what="bricks")
    self.file_name_trees = self.makeFileName(root, what="trees")
    self.brick_counter = {}

  def loadFromFile(self, project_name):
    """
    that's a bit tricky. We need the brick numbers for each tree
    """

    self.file_name_bricks = self.makeFileName(project_name, what="bricks")
    self.BRICK_GRAPHS, self.namespaces = self.__loadFromFile(self.file_name_bricks)

    self.file_name_trees = self.makeFileName(project_name, what="trees")
    exists = os.path.exists(self.file_name_trees)
    if exists:
      self.TREE_GRAPHS, _ = self.__loadFromFile(self.file_name_trees)

      for g in self.TREE_GRAPHS:
        i = -1
        graph = self.TREE_GRAPHS[g]
        for s, p, o in graph.triples((None, None, None)):
          # print(s,o)
          n = self.__extractNumber(s)
          m = self.__extractNumber(o)
          if n > i:
            i = n
          if m > i:
            i = m
        self.brick_counter[g] = i + 1
        # debugging("max integer", g, i)
    pass

  def __extractNumber(self, s):
    """
    that's a bit tricky. We need the brick numbers for each tree
    """
    n = "0"
    s = str(s)
    try:
      ss = s.split("#")[-1].split("_")[0]
    except:
      ss = None
    if ss.isnumeric():
      no = int(ss)
    else:
      no = -1
    return no

  def makeFileName(self, project_name, what=None):
    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, project_name) + "+%s." % what + FILE_FORMAT
    return file_name_bricks

  def __loadFromFile(self, file_name):
    data = ConjunctiveGraph("Memory")
    data.parse(file_name, format=FILE_FORMAT)

    GRAPHS = {}
    for i in data.contexts():
      Class = str(i.identifier).split("#")[-1]
      GRAPHS[Class] = data._graph(i.identifier)

    namespaces = {}
    for (prefix, namespace) in data.namespaces():
      namespaces[prefix] = namespace

    return GRAPHS, namespaces
    pass

  def makeDataTuplesForGraph(self, graphName, what):
    if what == "bricks":
      graph = self.BRICK_GRAPHS[graphName]
    else:
      graph = self.TREE_GRAPHS[graphName]
    debugging(graph.serialize(format="trig"))
    tuples_plus = []
    for subject, predicate, object in graph.triples((None, None, None)):
      debugging("--", subject, predicate, object)
      s = extractNameFromIRI(subject)
      p = MYTerms[predicate]
      o = extractNameFromIRI(object)
      if predicate in [RDFSTerms["is_defined_by"],
                       RDFSTerms["value"],
                       RDFSTerms["data_type"],
                       ] + RDF_PRIMITIVES:
        triple = s, p, o, -1
      else:
        triple = s, p, o, 1
      tuples_plus.append(triple)
    debugging("tuples", tuples_plus)
    return tuples_plus

  def getBrickList(self):
    return sorted(self.BRICK_GRAPHS.keys())

  def newBrickOrTreeGraph(self, what, brick_name):
    if what == "bricks":
      graphs = self.BRICK_GRAPHS
    else:
      graphs = self.TREE_GRAPHS
    graphs[brick_name] = Graph()
    # self.classURI = makeClassURI(brick_name)
    classURI = makeItemURI(brick_name, brick_name)
    itemURI = makeItemURI(brick_name, "")
    triple = (URIRef(classURI), RDFSTerms["is_class"], RDFSTerms["class"])
    graphs[brick_name].add(triple)
    graphs[brick_name].bind(brick_name, classURI)
    self.namespaces[brick_name] = classURI
    graphs[brick_name].bind(brick_name, itemURI)
    pass

  def getAllNamesInTheBrick(self, graphName, what):

    names = set()
    if what == "brick":
      g = self.BRICK_GRAPHS[graphName]
    elif what == "tree":
      g = self.TREE_GRAPHS[graphName]
    else:
      print(">>>>>>>>>>>> should not come here")
      return
    triple = (None, None, None)
    for subject, predicate, object in g.triples(triple):
      s = extractNameFromIRI(subject)
      o = extractNameFromIRI(object)
      names.add(s)
      names.add(o)
    return names

  def removeItem(self, what_type_of_graph, brick, item):
    subject = URIRef(makeItemURI(brick, item))
    triple = (subject, None, None)
    self.__removeItemFromGraph(what_type_of_graph, brick, subject, triple)

  def __removeItemFromGraph(self, what_type_of_graph, name, subject, triple):
    if what_type_of_graph == "bricks":
      graph = self.BRICK_GRAPHS[name]
    else:
      graph = self.TREE_GRAPHS[name]
    for t in graph.triples(triple):
      graph.remove(t)

    triple = (None, None, subject)
    for t in graph.triples(triple):
      graph.remove(t)

    triple = (subject, None, None)
    for t in graph.triples(triple):
      graph.remove(t)

  def addItem(self, Class, ClassOrSubClass, name):
    g = self.BRICK_GRAPHS[Class]
    self.__addItemToGraph(Class, ClassOrSubClass, g, name)

  def __addItemToGraph(self, Class, ClassOrSubClass, g, name):
    classURI = makeClassURI(Class)
    itemURI = makeItemURI(Class, "")
    if Class == ClassOrSubClass:
      o = URIRef(classURI)  # makeClassURI(Class))
    else:
      o = URIRef(itemURI + ClassOrSubClass)  # self.makeURI(Class, ClassOrSubClass)
    s = URIRef(itemURI + name)  # self.makeURI(Class, name)
    triple = (s, RDFSTerms["is_member"], o)
    g.add(triple)
    pass

  def addItemToTree(self, Class, ClassOrSubClass, name):
    g = self.TREE_GRAPHS[Class]
    self.__addItemToGraph(Class, ClassOrSubClass, g, name)

  def addPrimitive(self, Class, ClassOrSubClass, name, type):

    classURI = makeClassURI(Class)
    itemURI = makeItemURI(Class, "")
    if Class == ClassOrSubClass:
      s = URIRef(classURI) #URIRef(self.namespaces[Class])
    else:
      s = URIRef(itemURI + ClassOrSubClass)  # self.makeURI(Class, ClassOrSubClass)
    o = URIRef(itemURI + name)  # self.makeURI(Class, name)
    triple = (o, RDFSTerms["value"], s)
    self.BRICK_GRAPHS[Class].add(triple)
    oo = Literal("")
    triple = (oo, RDFSTerms[type], o)
    self.BRICK_GRAPHS[Class].add(triple)
    pass

  def modifyPrimitiveValue(self, tree_name, primitive_name, primitive_type, value):
    pass
    graph = self.TREE_GRAPHS[tree_name]
    primitive_uri = URIRef(makeItemURI(tree_name, primitive_name))
    triple = Literal(value), RDFSTerms[primitive_type], primitive_uri
    triple_search = None, RDFSTerms[primitive_type], primitive_uri
    for t in graph.triples(triple_search):
      print(t)
    if t:
      graph.remove(t)
      graph.add(triple)
    else:
      print(">>>>> should not come here")

  def renameBrick(self, oldName, newName):
    self.copyBrick("bricks", oldName, newName)
    del self.BRICK_GRAPHS[oldName]

  def renameTree(self, oldName, newName):
    self.TREE_GRAPHS[newName] = Graph()
    self.copyBrick("trees", oldName, newName)
    del self.TREE_GRAPHS[oldName]
    self.brick_counter[newName] = self.brick_counter[oldName]
    del self.brick_counter[oldName]

  def copyBrick(self, brickORtrees, oldName, newName):
    if brickORtrees == "bricks":
      what_graphs = self.BRICK_GRAPHS
    else:# brickORtrees == "trees":
      what_graphs = self.TREE_GRAPHS
    self.newBrickOrTreeGraph(brickORtrees, newName)
    new_graph = what_graphs[newName]
    self.namespaces[newName] = Namespace(makeItemURI(newName, newName))  # Namespace(makeClassURI(newName))
    old_graph = what_graphs[oldName]

    for s, p, o in old_graph.triples((None, None, None)):
      if p != RDFSTerms["is_class"]:
        s_new = s
        o_new = o
        if oldName in str(s):
          s_new = self.__renameURI(newName, oldName, s)
        if oldName in str(o):
          o_new = self.__renameURI(newName, oldName, o)
        triple = s_new, p, o_new
        new_graph.add(triple)
    pass

  def __renameURI(self, newName, oldName, uri):
    if uri.__class__ == rdflib.term.Literal:  # handle Literals
      return uri
    uri_name = extractNameFromIRI(uri)
    if uri_name == oldName:  # handle classes
      uri_name = newName

    uri_new = URIRef(makeItemURI(newName, uri_name))
    return uri_new

  def renameItem(self, brick, item, newName):
    g = self.BRICK_GRAPHS[brick]
    self.__renameItem(brick, g, item, newName)
    pass

  def renameItemInTree(self, brick, item, newName):
    g = self.TREE_GRAPHS[brick]
    self.__renameItem(brick, g, item, newName)
    pass

  def __renameItem(self, brick, g, item, newName):
    item_uri = URIRef(makeItemURI(brick, item))
    new_item_uri = URIRef(makeItemURI(brick, newName))
    triple = (item_uri, None, None)
    for s, p, o in g.triples(triple):
      g.remove((s, p, o))
      new_triple = (new_item_uri, p, o)
      g.add(new_triple)
    triple = None, None, item_uri
    for s, p, o in g.triples(triple):
      g.remove((s, p, o))
      new_triple = (s, p, new_item_uri)
      g.add(new_triple)

  def __attachBrick(self, brick_name, link_point, s_or_o, tree_name):
    counter = self.brick_counter[tree_name]
    brick_name_space = makeBrickNameSpace(brick_name, counter)
    s_or_o_new = s_or_o
    if brick_name in str(s_or_o):
      s_name = extractNameFromIRI(s_or_o)
      s_or_o_new = URIRef(self.tree_name_space_item + "%s_%s" % (counter, s_name))
    return s_or_o_new

  def linkBrickToItem(self, tree_name, tree_item_name, brick_name):
    tree_graph = self.TREE_GRAPHS[tree_name]
    brick_graph = self.BRICK_GRAPHS[brick_name]
    counter = self.brick_counter[tree_name]

    for s, p, o in brick_graph.triples((None, RDFSTerms["is_class"], None)):
      # rule: keep brick name
      self.tree_name_space = makeClassURI(tree_name)
      self.tree_name_space_item = makeItemURI(tree_name, "")
      s_ = URIRef(self.tree_name_space_item + "%s_%s" % (counter, brick_name))
      o_ = URIRef(self.tree_name_space_item + tree_item_name)
      triple = (s_,  # URIRef(self.tree_name_space_item + "%s"%self.brick_counter[tree_name],brick_name),
                RDFSTerms["is_defined_by"],
                o_)  # makeItemURI(tree_name, tree_item_name)))
      triple_ = triple[2], triple[1], triple[0]
      tree_graph.add(triple)
      pass

    for s, p, o in brick_graph.triples((None, None, None)):
      link_point = tree_item_name  # link_item_new_name
      if (p != RDFSTerms["is_class"]):  # or (brick_name in s):
        s_new = self.__attachBrick(brick_name,
                                   link_point,
                                   s,
                                   tree_name)
        o_new = self.__attachBrick(brick_name,
                                   link_point,
                                   o,
                                   tree_name)

        triple = s_new, p, o_new
        tree_graph.add(triple)
      else:
        print("class found s,p,o", s,p,o)   # note: adding linked node as class
        triple = s_, RDFSTerms["is_class"], RDFSTerms["class"]
        tree_graph.add(triple)
        pass
    self.brick_counter[tree_name] += 1
    pass

  def saveBricks(self, file_name=None):
    graphs = self.BRICK_GRAPHS
    conjunctiveGraph = self.__prepareConjunctiveGraph(graphs)
    if not file_name:
      file_name = self.file_name_bricks
    self.__writeQuadFile(conjunctiveGraph, file_name)
    pass

  def saveTrees(self, file_name=None):
    graphs = self.TREE_GRAPHS
    conjunctiveGraph = self.__prepareConjunctiveGraph(graphs)
    if not file_name:
      file_name = self.file_name_trees
    self.__writeQuadFile(conjunctiveGraph, file_name)
    pass

  def extractInstance(self, tree_name):
    graph = copy.deepcopy(self.TREE_GRAPHS[tree_name])

    keep_target = []
    for primitive in RDF_PRIMITIVES:
      triple = None, primitive, None
      for s, p, o in graph.triples(triple):
        if s != Literal(""):
          keep_target.append((s, p, o))

    root = URIRef(makeClassURI(tree_name))
    paths = set()
    for t in keep_target:
      path = find_path_back_triples(graph, t, root)

      print("found path")
      for triple in path:
        # print(triple)
        paths.add(triple)

    if paths != set():
      tree_name_instantiated = tree_name + "_i"

      self.tree_name_space = makeClassURI(tree_name_instantiated)
      self.tree_name_space_item = makeItemURI(tree_name_instantiated, "")

      self.brick_counter[tree_name_instantiated] = 0
      g = self.TREE_GRAPHS[tree_name_instantiated] = Graph("Memory")

      classURI = makeClassURI(tree_name_instantiated)
      self.namespaces[tree_name_instantiated] = classURI
      triple = (URIRef(classURI), RDFSTerms["is_class"], RDFSTerms["class"])
      self.TREE_GRAPHS[tree_name_instantiated].add(triple)

      self.TREE_GRAPHS[tree_name_instantiated].bind(tree_name_instantiated,
                                                    self.tree_name_space)
      self.TREE_GRAPHS[tree_name_instantiated].bind(tree_name_instantiated,
                                                    self.tree_name_space_item)
      pass
      for s, p, o in paths:
        s_new = self.__renameURI(tree_name_instantiated, tree_name, s)
        o_new = self.__renameURI(tree_name_instantiated, tree_name, o)
        g.add((s_new, p, o_new))

    pass
    return

  def __prepareConjunctiveGraph(self, graphs):
    pass
    conjunctiveGraph = ConjunctiveGraph("Memory")
    for cl in graphs:
      for s, p, o in graphs[cl].triples((None, None, None)):
        itemURI = makeItemURI(cl, "")
        classURI = makeClassURI(cl)
        # conjunctiveGraph.bind(cl + "_I", itemURI)
        conjunctiveGraph.bind(cl, itemURI)
        # conjunctiveGraph.bind(cl, classURI)
        conjunctiveGraph.get_context(classURI).add((s, p, o))
    return conjunctiveGraph

  def newTree(self, tree_name, brick_name):
    brick = self.BRICK_GRAPHS[brick_name]
    copy_brick = copy.deepcopy(brick)

    self.renameBrick(brick_name, tree_name)
    named_brick = self.BRICK_GRAPHS[tree_name]
    self.TREE_GRAPHS[tree_name] = copy.deepcopy(named_brick)

    classURI = makeClassURI(tree_name)
    self.namespaces[tree_name] = classURI
    triple = (URIRef(classURI), RDFSTerms["is_class"], RDFSTerms["class"])
    self.TREE_GRAPHS[tree_name].add(triple)

    self.tree_name_space = makeClassURI(tree_name)
    self.tree_name_space_item = makeItemURI(tree_name, "")

    self.brick_counter[tree_name] = 0
    self.TREE_GRAPHS[tree_name].bind(tree_name,
                                     self.tree_name_space)
    self.TREE_GRAPHS[tree_name].bind(tree_name,
                                     self.tree_name_space_item)

    # clean up bricks
    self.BRICK_GRAPHS[brick_name] = copy_brick
    del self.BRICK_GRAPHS[tree_name]
    pass

  def getTreeList(self):
    tree_list = sorted(self.TREE_GRAPHS.keys())
    return tree_list

  def __writeQuadFile(self, conjunctiveGraph, f):
    saveBackupFile(f)
    inf = open(f, "w")
    inf.write(conjunctiveGraph.serialize(format=FILE_FORMAT))
    inf.close()
    print("written to file ", f)

    fs = f + "_"
    inf = open(fs, "w")
    inf.write(conjunctiveGraph.serialize(format="turtle"))
    inf.close()
