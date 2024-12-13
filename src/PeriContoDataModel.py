import os
import sys

from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from PeriContoSemantics import CLASS_SEPARATOR
from PeriContoSemantics import FILE_FORMAT
from PeriContoSemantics import ITEM_SEPARATOR
from PeriContoSemantics import MYTerms
from PeriContoSemantics import ONTOLOGY_REPOSITORY
from PeriContoSemantics import PERICONTO
from PeriContoSemantics import PRIMITIVES
from PeriContoSemantics import RDFSTerms
from PeriContoSemantics import RDF_PRIMITIVES
from PeriContoSemantics import ROOTCLASS
from PeriContoSemantics import extract_name_from_class_uri

DEBUGG = True


def debugging(*info):
  if DEBUGG:
    print("debugging", info)


def getFilesAndVersions(abs_name, ext):
  base_name = os.path.basename(abs_name)
  ver = 0  # initial last version
  _s = []
  directory = os.path.dirname(abs_name)  # listdir(os.getcwd())
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
  else:
    print("Error -- no such file : %s" % path, file=sys.stderr)
    return


class DataEnumerators:
  """
  counters for data -- makes the name unique
  """

  def __init__(self):
    self.counters = {}
    for p in PRIMITIVES:
      self.counters[p] = -1

  def setCounter(self, p, value):
    if p not in PRIMITIVES:
      print(">>>>>>> oops -- no such counter %s", p)
      return
    self.counters[p] = value

  def incrementCounter(self, p):
    if p not in PRIMITIVES:
      print(">>>>>>> oops -- no such counter %s", p)
      return
    self.counters[p] += 1
    return self.counters[p]


class DataModel:
  def __init__(self, root):
    self.namespaces = {
            ROOTCLASS: Namespace(PERICONTO),
            # DATACLASS: Namespace(DATA),
            }

    self.data_counters = DataEnumerators()
    self.BRICK_GRAPHS = {}
    self.TREE_GRAPHS = {}
    # for space in self.namespaces:
    #  self.addClass(space)
    if root:
      self.newBrick(root)

  def loadFromFile(self, project_name):

    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, project_name) + "+bricks." + FILE_FORMAT
    self.BRICK_GRAPHS, self.namespaces = self.__loadFromFile(file_name_bricks)

    file_name_trees = os.path.join(ONTOLOGY_REPOSITORY, project_name) + "+trees." + FILE_FORMAT
    exists = os.path.exists(file_name_trees)
    if exists:
      self.TREE_GRAPHS, _ = self.__loadFromFile(file_name_trees)

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

  def makeBrickDataTuples(self):
    dataTuples = {}
    for graphName in self.BRICK_GRAPHS:
      dataTuples[graphName] = self.makeDataTuplesForGraph(graphName, "bricks")
    return dataTuples

  def makeDataTuplesForGraph(self, graphName, what):
    if what == "bricks":
      graph = self.BRICK_GRAPHS[graphName]
    else:
      graph = self.TREE_GRAPHS[graphName]
    debugging(graph.serialize(format="turtle"))
    # print("debugging", origin)
    tuples_plus = []
    for subject, predicate, object in graph.triples((None, None, None)):
      debugging("--", subject, predicate, object)
      if not ITEM_SEPARATOR in subject:
        s = str(subject).split(CLASS_SEPARATOR)[-1]
      else:
        s = extract_name_from_class_uri(subject)
      p = MYTerms[predicate]
      if not ITEM_SEPARATOR in object:
        o = str(object).split(CLASS_SEPARATOR)[-1]
      else:
        o = extract_name_from_class_uri(object)

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

  def removeItem(self, brick, item):
    subject = self.makeURI(brick, item)
    triple = (subject, None, None)
    for t in self.BRICK_GRAPHS[brick].triples(triple):
      self.BRICK_GRAPHS[brick].remove(t)
    triple = (None,None,subject)
    for t in self.BRICK_GRAPHS[brick].triples(triple):
      self.BRICK_GRAPHS[brick].remove(t)

  def makeURI(self, Class, identifier):
    uri = URIRef(self.namespaces[Class] + "#" + identifier)
    return uri

  def addItem(self, Class, ClassOrSubClass, name):
    if Class == ClassOrSubClass:
      _, o = self.makeClassURI(Class)
    else:
      o = self.makeURI(Class, ClassOrSubClass)
    s = self.makeURI(Class, name)

    triple = (s, RDFSTerms["is_member"], o)
    self.addElucidation(Class, s)
    self.GRAPHS[Class].add(triple)
    pass



  # def what_type_of_brick_item_is_this(self, brick_name, item_name):
  #   if brick_name == item_name:
  #     return "class"
  #   s = URIRef(self.namespaces[brick_name]+"#", item_name)
  #   triple = s,None,None
  #   for s,p,o in self.BRICK_GRAPHS[brick_name].triples(triple):
  #     print(s,p,o)



  def __makeURIForClass(self, name):
    return URIRef(PERICONTO + name)
  # 
  # def __removePrimitive(self, Class, predicate_ID, primitive):
  #   subject = self.makeURI(Class, primitive)
  #   triple = (subject, RDFSTerms[predicate_ID], None)
  #   for t in self.GRAPHS[Class].triples(triple):
  #     self.GRAPHS[Class].remove(t)
  # 
  # def makeURI(self, Class, identifier):
  #   try:
  #     uri = URIRef(self.namespaces[Class] + "#" + identifier)
  #   except:
  #     pass
  #   # print("uri: ", identifier, "-->", uri)
  #   return uri
  # 
  # def makeClassURI(self, Class):
  #   uid = "%s/%s" % (BASE, Class)
  #   uris = URIRef(uid)
  #   return uid, uris
  # 
  # # def loadFromFile(self, file_name):
  # #   data = ConjunctiveGraph("Memory")
  # #   data.parse(file_name, format=FILE_FORMAT)
  # #
  # #   self.GRAPHS = {}
  # #   for i in data.contexts():
  # #     Class = str(i.identifier).split("/")[-1]
  # #     self.GRAPHS[Class] = data._graph(i.identifier)
  # #
  # #   self.namespaces = {}
  # #   for (prefix, namespace) in data.namespaces():
  # #     self.namespaces[prefix] = namespace
  # 
  # def getClassNamesList(self):
  #   return list(self.GRAPHS.keys())
  # 
  # def getSubClassList(self, Class):
  #   triple = (None, RDFSTerms["is_member"], None)
  #   return [extract_name_from_class_uri(s) for s, p, o in self.GRAPHS[Class].triples(triple)]
  # 
  # def getAllLinkedClasses(self):
  #   accumulator = set()
  #   for c in self.GRAPHS:
  #     triple = None, RDFSTerms["is_defined_by"], None
  #     for t in self.GRAPHS[c].triples(triple):
  #       _, _, o = t
  #       accumulator.add(self.extractNameFromObject(o))
  #   return accumulator
  # 
  # def extractNameFromObject(self, object):
  #   if ITEM_SEPARATOR in object:
  #     return extract_name_from_class_uri(object)
  #   elif CLASS_SEPARATOR in object:
  #     return extract_class_name(object)
  # 
  # def getLinkList(self, Class, name):
  #   object = self.makeURI("ROOT", name)
  #   triple = (object, RDFSTerms["is_defined_by"], None)
  #   return [extract_name_from_class_uri(o) for s, p, o in self.GRAPHS[Class].triples(triple)]
  # 
  # def getIntegerList(self, Class):
  #   triple = (None, RDFSTerms["integer"], None)
  #   return [extract_name_from_class_uri(o) for s, p, o in self.GRAPHS[Class].triples(triple)]
  # 
  # def getStringList(self, Class):
  #   triple = (None, RDFSTerms["string"], None)
  #   return [extract_name_from_class_uri(s) for s, p, o in self.GRAPHS[Class].triples(triple)]
  # 
  # def getValueList(self, Class):
  #   triple = (None, RDFSTerms["value"], None)
  #   return [extract_name_from_class_uri(o) for s, p, o in self.GRAPHS[Class].triples(triple)]
  # 
  # def getElucidationList(self, Class):
  #   triple = (None, RDFSTerms["comment"], None)
  #   return [s for s, p, o in self.GRAPHS[Class].triples(triple)]
  # 
  # def getAllNames(self, Class):
  #   triple = (None, None, None)
  # 
  #   return {extract_name_from_class_uri(s) for s, p, o in self.GRAPHS[Class].triples(triple)}
  #   # return [str(s).split(":")[-1] for c in self.GRAPHS for s,p,o in self.GRAPHS[c].triples(triple)]
  # 
  # def addClass(self, Class):
  #   uid, uris = self.makeClassURI(Class)
  #   self.namespaces[Class] = Namespace(uid)
  #   self.GRAPHS[Class] = Graph("Memory", uris)  # uid)
  #   self.GRAPHS[Class].bind(Class, self.namespaces[Class])
  #   sub = URIRef(uid)
  #   triple = (sub, RDFSTerms["is_class"], RDFSTerms["class"])
  #   self.GRAPHS[Class].add(triple)
  #   self.addElucidation(Class, sub)
  # 
  #   return self.getClassNamesList()
  # 
  # def addElucidation(self, Class, sub):
  #   # name = self.extractNameFromObject(sub)
  #   no = self.data_counters.incrementCounter("comment")
  #   o = URIRef(self.namespaces[Class] + "#elucidation-%s" % no)
  #   # triple = (sub, RDFSTerms["value"], RDFSTerms["comment"])
  #   triple = (sub, RDFSTerms["data_type"], o)
  #   self.GRAPHS[Class].add(triple)
  #   triple = (o, RDFSTerms["value"], RDFSTerms["comment"])
  #   self.GRAPHS[Class].add(triple)
  # 
  # def checkForClassIsUsed(self, Class):
  #   current_set_of_classes = set(self.GRAPHS.keys())
  #   found = 0
  #   uri = self.makeURI("ROOT", Class)
  #   for c in current_set_of_classes:
  #     triple = (None, None, uri)
  #     for t in self.GRAPHS[c].triples(triple):
  #       found += 1
  # 
  #   if found == 0:
  #     dialog = makeMessageBox("remove class %s" % Class, buttons=["NO", "YES"])
  #     if dialog == "YES":
  #       self.removeClass(Class)
  # 
  # def removeClass(self, Class):
  #   for c in self.getClassNamesList():
  #     classURI = self.makeURI(c, Class)
  #     graph = self.GRAPHS[c]
  #     triple = (None, RDFSTerms["is_defined_by"], classURI)
  #     for t in graph.triples(triple):
  #       graph.remove(t)
  #   del self.GRAPHS[Class]
  # 
  #   # self.removeAllLinksToClass(Class)
  #   return self.getClassNamesList()
  # 
  # def addSubclass(self, Class, ClassOrSubClass, name):
  #   if Class == ClassOrSubClass:
  #     _, o = self.makeClassURI(Class)
  #   else:
  #     o = self.makeURI(Class, ClassOrSubClass)
  #   s = self.makeURI(Class, name)
  # 
  #   triple = (s, RDFSTerms["is_member"], o)
  #   self.addElucidation(Class, s)
  #   self.GRAPHS[Class].add(triple)
  #   pass
  # 
  # def removeSubClass(self, Class, item):
  #   s = self.makeURI(Class, item)
  #   triple = s, RDFSTerms["is_member"], None
  #   for t in self.GRAPHS[Class].triples(triple):
  #     self.GRAPHS[Class].remove(t)
  #     pass
  # 
  # def addPrimitive(self, Class, ClassOrSubClass, name, type):
  #   no = self.data_counters.incrementCounter(type)
  #   o = self.makeURI(Class, name + "-%s" % no)
  #   s = self.makeURI(Class, ClassOrSubClass)
  #   p = RDFSTerms["value"]
  #   triple = s, p, o
  #   self.GRAPHS[Class].add(triple)
  #   sv = o  # self.makeURI(Class, name)
  #   p = RDFSTerms["data_type"]
  #   ov = RDFSTerms[type]  # self.makeURI(Class, name) #s
  #   # triple = s,p,ov
  #   triple = sv, p, ov
  #   self.GRAPHS[Class].add(triple)
  # 
  # # def addElucidation(self, elucidation, Class, name):
  # #
  # #   s = self.makeURI(Class, name)
  # #   p = RDFSTerms["value"]
  # #   o = self.makeURI(Class, "elucidation")
  # #   triple = s, p, o
  # #   self.GRAPHS[Class].add(triple)
  # #   # p = RDFSTerms["data_type"]
  # #   # ov = RDFSTerms["string"]
  # #   # triple = s, p, ov    # self.GRAPHS[Class].add(triple)
  # #   # p = "elucidation"
  # #   oe = rdflib.term.Literal(elucidation, lang="en")
  # #   # oe = Literal("Literal\elucidation", lang="en")
  # #   triple = o, p, oe
  # #   self.GRAPHS[Class].add(triple)
  # 
  # def addLink(self, Class, obj, subj):
  #   subject = self.makeURI(Class, subj)
  #   object = self.makeURI(Class, obj)
  #   predicate = RDFSTerms["is_defined_by"]
  #   self.GRAPHS[Class].add((subject, predicate, object))
  # 
  # def removeLinkInClass(self, Class, item):
  # 
  #   o_name = self.getLinkList(Class, item)[0]
  #   object = self.makeURI(Class, o_name)
  # 
  #   subject = self.makeURI("ROOT", item)
  #   triple = (subject, RDFSTerms["is_defined_by"], object)
  # 
  #   # triple = (None, RDFSTerms["is_defined_by"], object)
  #   for s, p, o in self.GRAPHS[Class].triples(triple):
  #     object = extract_name_from_class_uri(o)
  #   self.GRAPHS[Class].remove(triple)
  #   return object
  # 
  # def removePrimitive(self, Class, primitive):
  #   graph = self.GRAPHS[Class]
  #   primitiveURI = self.makeURI(Class, primitive)
  #   for t in graph.triples((None, None, primitiveURI)):
  #     graph.remove(t)
  #   for t in graph.triples((primitiveURI, None, None)):
  #     graph.remove(t)
  #   pass
  # 
  # def isRoot(self, name):
  #   return name == ROOTCLASS
  # 
  # def isClass(self, name):
  #   l = self.getClassNamesList()
  #   return name in l
  # 
  # def isSubClass(self, Class, name):
  #   l = self.getSubClassList(Class)
  #   return name in l
  # 
  # def isLinkedWidth(self, Class, name):
  #   l = self.getLinkList(Class, name)
  #   return l != []
  # 
  # def isPrimitive(self, Class, name):
  #   return name in PRIMITIVES
  # 
  # def isInteger(self, Class, name):
  #   return name in self.getIntegerList(Class)
  # 
  # def isString(self, Class, name):
  #   return name in self.getStringList(Class)
  # 
  # def isElucidation(self, Class, name):
  #   # uri = self.makeURI(Class, name)
  #   return "elucidation" in name
  # 
  # def isValue(self, Class, name):
  #   return name in self.getValueList(Class)
  # 
  # def what_is_this(self, Class, name):
  #   what = []
  #   if self.isClass(name) or (name == "Class"): what.append("class")
  #   if self.isSubClass(Class, name): what.append("is_member")
  #   if self.isInteger(Class, name): what.append("integer")
  #   if self.isString(Class, name): what.append("string")
  #   if self.isValue(Class, name): what.append("value")
  #   if self.isElucidation(Class, name): what.append("elucidation")
  #   if self.isLinkedWidth(Class, name): what.append("linked")
  #   return what