import copy
import os
import re

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

DEBUGG = True


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
        for s,p,o in graph.triples((None,None,None)):
          print(s,o)
          n = self.__extractNumber(s)
          m = self.__extractNumber(o)
          if n > i:
            i = n
          if m > i:
            i = m
        self.brick_counter[g] = i +1
        debugging("max integer", g, i)
    pass

  def __extractNumber(self, s):
    """
    that's a bit tricky. We need the brick numbers for each tree
    """
    n = "0"
    s = str(s)
    try:
      ss = s.split("#")[-1].split("_")[0]
      print(ss)
    except:
      ss = None
    if ss.isnumeric():
      no = int(ss)
    else:
      no = -1
    # for i in str(ss):
    #   if i.isnumeric():
    #     n += i
    print(n, int(n))
    return no

  def makeFileName(self, project_name, what=None):
    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, project_name) + "+%s." % what + FILE_FORMAT
    return file_name_bricks

  def __loadFromFile(self, file_name):
    data = ConjunctiveGraph("Memory")
    data.parse(file_name, format=FILE_FORMAT)

    GRAPHS = {}
    for i in data.contexts():
      Class = str(i.identifier).split("/")[-1]
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
        triple = o, p, s, -1
      else:
        triple = s, p, o, 1
      tuples_plus.append(triple)
    debugging("tuples", tuples_plus)
    return tuples_plus

  def getBrickList(self):
    return sorted(self.BRICK_GRAPHS.keys())

  def newBrick(self, brick_name):
    self.BRICK_GRAPHS[brick_name] = Graph()
    self.classURI = makeClassURI(brick_name)
    self.itemURI = makeItemURI(brick_name,"")
    triple = (URIRef(self.classURI), RDFSTerms["is_class"], RDFSTerms["class"])
    self.BRICK_GRAPHS[brick_name].add(triple)
    self.BRICK_GRAPHS[brick_name].bind(brick_name, self.classURI)
    self.namespaces[brick_name] = self.classURI #self.itemURI
    self.BRICK_GRAPHS[brick_name].bind(brick_name, self.itemURI)
    # self.namespaces[brick_name] = [self.classURI, self.itemURI]
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

  def removeItem(self, brick, item):
    subject = self.makeURI(brick, item)
    triple = (subject, None, None)
    for t in self.BRICK_GRAPHS[brick].triples(triple):
      self.BRICK_GRAPHS[brick].remove(t)
    triple = (None, None, subject)
    for t in self.BRICK_GRAPHS[brick].triples(triple):
      self.BRICK_GRAPHS[brick].remove(t)

  def makeURI(self, Class, identifier):
    uri = URIRef(self.namespaces[Class] + "#" + identifier)
    return uri

  def addItem(self, Class, ClassOrSubClass, name):
    g = self.BRICK_GRAPHS[Class]
    self.__addItemToGraph(Class, ClassOrSubClass, g, name)

  def __addItemToGraph(self, Class, ClassOrSubClass, g, name):
    self.classURI = makeClassURI(Class)
    self.itemURI = makeItemURI(Class, "")
    if Class == ClassOrSubClass:
      o = URIRef(self.classURI)  # makeClassURI(Class))
    else:
      o = URIRef(self.itemURI + ClassOrSubClass)  # self.makeURI(Class, ClassOrSubClass)
    s = URIRef(self.itemURI + name)  # self.makeURI(Class, name)
    triple = (s, RDFSTerms["is_member"], o)
    g.add(triple)
    pass

  def addItemToTree(self, Class, ClassOrSubClass, name):
    g = self.TREE_GRAPHS[Class]
    self.__addItemToGraph(Class, ClassOrSubClass, g, name)

  def addPrimitive(self, Class, ClassOrSubClass, name, type):

    self.classURI = makeClassURI(Class)
    self.itemURI = makeItemURI(Class,"")
    if Class == ClassOrSubClass:
      s = URIRef(self.namespaces[Class])
    else:
      s = URIRef(self.itemURI+ClassOrSubClass)  #self.makeURI(Class, ClassOrSubClass)
    o = URIRef(self.itemURI + name) #self.makeURI(Class, name)
    triple = (s, RDFSTerms["value"], o)
    self.BRICK_GRAPHS[Class].add(triple)
    oo = Literal("")
    triple = (o, RDFSTerms[type], oo)
    self.BRICK_GRAPHS[Class].add(triple)
    pass

  def renameBrick(self, oldName, newName):
    self.copyBrick(self.BRICK_GRAPHS, oldName, newName)
    del self.BRICK_GRAPHS[oldName]

  def renameTree(self, oldName, newName):
    self.TREE_GRAPHS[newName] = Graph()
    self.copyBrick(self.TREE_GRAPHS, oldName, newName)
    del self.TREE_GRAPHS[oldName]
    self.brick_counter[newName] = self.brick_counter[oldName]
    del self.brick_counter[oldName]

  def copyBrick(self, what_graphs, oldName, newName):
    self.newBrick(newName)
    # self.BRICK_GRAPHS[newName] = Graph()
    new_graph = what_graphs[newName]
    self.namespaces[newName] = Namespace(makeClassURI(newName))
    old_graph = what_graphs[oldName]

    for s, p, o in old_graph.triples((None, None, None)):
      if p != RDFSTerms["is_class"]:
        s_new = s
        o_new = o
        if oldName in str(s):
          s_name = extractNameFromIRI(s)
          if (oldName in s) and ("#" in s):
            s_new = URIRef(makeItemURI(newName, s_name))
          else:
            s_new = URIRef(makeClassURI(newName))
        if oldName in str(o):
          o_name = extractNameFromIRI(o)
          if (oldName in o) and ("#" in o):
            o_new = URIRef(makeItemURI(newName, o_name))
          else:
            o_new = URIRef(makeClassURI(newName))
        triple = s_new, p, o_new
        print("new triple", triple)
        new_graph.add(triple)
    pass

  def renameItem(self, brick, item, newName):
    item_uri = URIRef(makeItemURI(brick, item))
    new_item_uri = URIRef(makeItemURI(brick, newName))
    g = self.BRICK_GRAPHS[brick]
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
    pass

  def __attachBrick(self, brick_name, link_point, s_or_o, tree_name):
    counter = self.brick_counter[tree_name]
    brick_name_space = makeBrickNameSpace(brick_name, counter)
    s_or_o_new = s_or_o
    if brick_name in str(s_or_o):
      s_name = extractNameFromIRI(s_or_o)
      # s_or_o_new = URIRef(brick_name_space + "%s_%s"%(counter,s_name))
      s_or_o_new = URIRef(self.tree_name_space_item + "%s_%s"%(counter,s_name))
    return s_or_o_new

  def linkBrickToItem(self, tree_name, tree_item_name, brick_name):
    tree_graph = self.TREE_GRAPHS[tree_name]
    brick_graph = self.BRICK_GRAPHS[brick_name]
    counter = self.brick_counter[tree_name]

    for s, p, o in brick_graph.triples((None, RDFSTerms["is_class"], None)):
      # rule: keep brick name
      # brick_name_space = makeBrickNameSpace(brick_name,
      #                                       self.brick_counter[tree_name])
      # tree_graph.bind(brick_name + "_%s" % self.brick_counter[tree_name], brick_name_space)

      self.tree_name_space = makeClassURI(tree_name)
      self.tree_name_space_item = makeItemURI(tree_name, "")
      # triple = (URIRef(brick_name_space + "%s_%s"%(counter,brick_name)),
      # URIRef(self.tree_name_space_item + "%s_%s" % (counter, s_name))
      triple = (URIRef(self.tree_name_space_item + "%s_%s"%(counter,brick_name)), #URIRef(self.tree_name_space_item + "%s"%self.brick_counter[tree_name],brick_name),
                RDFSTerms["is_defined_by"],
                URIRef(self.tree_name_space_item + tree_item_name)) #makeItemURI(tree_name, tree_item_name)))
      triple_ = triple[2], triple[1], triple[0]
      tree_graph.add(triple_)
      pass

    for s, p, o in brick_graph.triples((None, None, None)):
      link_point = tree_item_name # link_item_new_name
      print("s,o,p", s,o,p)
      if (p != RDFSTerms["is_class"]): # or (brick_name in s):
        s_new = self.__attachBrick(brick_name,
                                   link_point,
                                   s,
                                   tree_name)
        o_new = self.__attachBrick(brick_name,
                                   link_point,
                                   o,
                                   tree_name)

        triple = s_new, p, o_new
        print("old triple", s,p,o)
        print("new triple", triple)
        tree_graph.add(triple)
      else:
        print("class found s,p,o", s,p,o)
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

  def __prepareConjunctiveGraph(self, graphs):
    pass
    # namespaces = set()
    # n = []
    # for g in graphs:
    #   n = set()
    #   for i in graphs[g].namespaces():
    #     n.add(i)
    #
    # namespaces = list(n)
    conjunctiveGraph = ConjunctiveGraph("Memory")
    name_spaces = self.namespaces
    # name_spaces = {}
    # for pre, ns in namespaces:
    #   conjunctiveGraph.bind(pre, ns )#ns, namespaces[ns])
    #   name_spaces[pre] = ns
    for cl in graphs:
      for s, p, o in graphs[cl].triples((None, None, None)):
        conjunctiveGraph.get_context(name_spaces[cl]).add((s, p, o))
        itemURI = makeItemURI(cl, "")
        conjunctiveGraph.bind(cl+"_I", itemURI)
        conjunctiveGraph.bind(cl,name_spaces[cl])
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

    # brick_name_space = makeItemURI(brick_name,"")
    self.tree_name_space = makeClassURI(tree_name)
    self.tree_name_space_item = makeItemURI(tree_name, "")

    self.brick_counter[tree_name] = 0
    # self.TREE_GRAPHS[tree_name].bind(tree_name + "_%s" % self.brick_counter[tree_name],
    #                                  brick_name_space)
    self.TREE_GRAPHS[tree_name].bind(tree_name ,
                                     self.tree_name_space)
    self.TREE_GRAPHS[tree_name].bind(tree_name ,
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
