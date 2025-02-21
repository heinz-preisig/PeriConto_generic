#!/usr/local/bin/python3

"""
This version uses RDF syntax for the predicates. The subjects and objects are Literals. The latter caused problems
when saving using the serializers. It can be saved but not read afterwards.

So the approach is to use an internal representation of the predicates and translate when loading and saving.


"""
import copy
import glob
import os
import sys

from rdflib import Namespace

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *
from graphviz import Digraph
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import RDF
from rdflib import URIRef
from rdflib import XSD
from rdflib import namespace
# from rdflib.namespace import RDFS

# from graphHAP import Graph
from PeriContoSchemaBricks_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String
from resources.ui_single_list_selector_impl import UI_stringSelector

# https://www.w3.org/TR/rdf12-concepts/#dfn-rdf-dataset
# https://www.w3.org/TR/rdf-schema/#ch_resource

RDFS = namespace.RDFS
BASE = "http://example.org"
ITEM_SEPARATOR = "#"
CLASS_SEPARATOR = "/"
PERICONTO = BASE + ITEM_SEPARATOR
DATA = BASE + "data/" + ITEM_SEPARATOR

ONTOLOGY_REPOSITORY = "../ontologyRepository"
ROOTCLASS = "ROOT"
DATACLASS = "DATA"

COMMENT = "comment"
ELUCIDATION = "elucidation"

FILE_FORMAT = "trig"
FILE_FORMAT_ = "json-ld"

RDFSTerms = {
        "class"        : RDFS.Class,
        "is_class"     : RDF.type,  # was "is_type"
        "is_member"    : RDFS.member,
        "is_defined_by": RDFS.isDefinedBy,
        "value"        : RDF.value,
        "data_type"    : RDFS.Datatype,
        "comment"      : RDFS.comment,
        "integer"      : XSD.integer,
        "string"       : XSD.string,
        "decimal"      : XSD.decimal,
        "uri"          : XSD.anyURI,
        "label"        : RDFS.label,
        "boolean"      : XSD.boolean,
        }

MYTerms = {v: k for k, v in RDFSTerms.items()}

PRIMITIVES = ["integer", "comment", "string", "decimal", "uri", "boolean"]
ADD_ELUCIDATIONS = ["class", "is_member", "value"]

COLOURS = {
        "ROOT"         : QtGui.QColor(0, 199, 255),
        "is_member"    : QtGui.QColor(0, 0, 0, 255),
        "is_defined_by": QtGui.QColor(255, 100, 5, 255),
        "value"        : QtGui.QColor(230, 165, 75),
        "data_type"    : QtGui.QColor(100, 100, 100),
        "comment"      : QtGui.QColor(155, 155, 255),
        "integer"      : QtGui.QColor(155, 155, 255),
        "string"       : QtGui.QColor(255, 200, 200, 255),
        "selected"     : QtGui.QColor(252, 248, 192, 255),
        "unselect"     : QtGui.QColor(255, 255, 255, 255),
        }

QBRUSHES = {}
for c_hash in COLOURS.keys():
  QBRUSHES[c_hash] = QtGui.QBrush(COLOURS[c_hash])

DIRECTION = {
        "is_member"    : 1,
        "is_defined_by": 1,
        "value"        : -1,
        "comment"      : -1,
        "integer"      : -1,
        "string"       : -1,
        # "type"            : -1,
        }

LINK_COLOUR = QtGui.QColor(255, 100, 5, 255)
PRIMITIVE_COLOUR = QtGui.QColor(255, 3, 23, 255)


def extract_name_from_class_uri(uri):
  return uri.split(ITEM_SEPARATOR)[-1]


def extract_class_name(uri):
  return uri.split(CLASS_SEPARATOR)[-1]

DEBUGG = True
def debugging(*info):
  if DEBUGG:
    print("debugging", info)


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

  def __init__(self, graph_name, graph_tripples, class_names):
    self.classes = class_names
    self.tripples = graph_tripples
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

  def addEdge(self, From, To, type):
    try:
      colour = self.EDGE_COLOURS[type]
    except:
      colour = self.EDGE_COLOURS["other"]
    self.dot.edge(From, To,
                  color=colour,
                  label=type
                  )


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


class DataModel():
  def __init__(self, root):
    self.namespaces = {
            ROOTCLASS: Namespace(PERICONTO),
            DATACLASS: Namespace(DATA),
            }

    self.data_counters = DataEnumerators()
    self.GRAPHS = {}
    # for space in self.namespaces:
    #  self.addClass(space)
    self.addClass(root)

  def __makeURIForClass(self, name):
    return URIRef(PERICONTO + name)

  def __removePrimitive(self, Class, predicate_ID, primitive):
    subject = self.makeURI(Class, primitive)
    triple = (subject, RDFSTerms[predicate_ID], None)
    for t in self.GRAPHS[Class].triples(triple):
      self.GRAPHS[Class].remove(t)

  def makeURI(self, Class, identifier):
    try:
      uri = URIRef(self.namespaces[Class] + "#" + identifier)
    except:
      pass
    # print("uri: ", identifier, "-->", uri)
    return uri

  def makeClassURI(self, Class):
    uid = "%s/%s" % (BASE, Class)
    uris = URIRef(uid)
    return uid, uris

  def loadFromFile(self, file_name):
    data = ConjunctiveGraph("Memory")
    data.parse(file_name, format=FILE_FORMAT)

    self.GRAPHS = {}
    for i in data.contexts():
      Class = str(i.identifier).split("/")[-1]
      self.GRAPHS[Class] = data._graph(i.identifier)

    self.namespaces = {}
    for (prefix, namespace) in data.namespaces():
      self.namespaces[prefix] = namespace

  def getClassNamesList(self):
    return list(self.GRAPHS.keys())

  def getSubClassList(self, Class):
    triple = (None, RDFSTerms["is_member"], None)
    return [extract_name_from_class_uri(s) for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getAllLinkedClasses(self):
    accumulator = set()
    for c in self.GRAPHS:
      triple = None, RDFSTerms["is_defined_by"], None
      for t in self.GRAPHS[c].triples(triple):
        _, _, o = t
        accumulator.add(self.extractNameFromObject(o))
    return accumulator

  def extractNameFromObject(self, object):
    if ITEM_SEPARATOR in object:
      return extract_name_from_class_uri(object)
    elif CLASS_SEPARATOR in object:
      return extract_class_name(object)

  def getLinkList(self, Class, name):
    object = self.makeURI("ROOT", name)
    triple = (object, RDFSTerms["is_defined_by"], None)
    return [extract_name_from_class_uri(o) for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getIntegerList(self, Class):
    triple = (None, RDFSTerms["integer"], None)
    return [extract_name_from_class_uri(o) for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getStringList(self, Class):
    triple = (None, RDFSTerms["string"], None)
    return [extract_name_from_class_uri(s) for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getValueList(self, Class):
    triple = (None, RDFSTerms["value"], None)
    return [extract_name_from_class_uri(o) for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getElucidationList(self, Class):
    triple = (None, RDFSTerms["comment"], None)
    return [s for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getAllNames(self, Class):
    triple = (None, None, None)

    return {extract_name_from_class_uri(s) for s, p, o in self.GRAPHS[Class].triples(triple)}
    # return [str(s).split(":")[-1] for c in self.GRAPHS for s,p,o in self.GRAPHS[c].triples(triple)]

  def addClass(self, Class):
    uid, uris = self.makeClassURI(Class)
    self.namespaces[Class] = Namespace(uid)
    self.GRAPHS[Class] = Graph("Memory", uris)  # uid)
    self.GRAPHS[Class].bind(Class, self.namespaces[Class])
    sub = URIRef(uid)
    triple = (sub, RDFSTerms["is_class"], RDFSTerms["class"])
    self.GRAPHS[Class].add(triple)
    self.addElucidation(Class, sub)

    return self.getClassNamesList()

  def addElucidation(self, Class, sub):
    # name = self.extractNameFromObject(sub)
    no = self.data_counters.incrementCounter("comment")
    o = URIRef(self.namespaces[Class] + "#elucidation-%s" % no)
    # triple = (sub, RDFSTerms["value"], RDFSTerms["comment"])
    triple = (sub, RDFSTerms["data_type"], o)
    self.GRAPHS[Class].add(triple)
    triple = (o, RDFSTerms["value"], RDFSTerms["comment"])
    self.GRAPHS[Class].add(triple)

  def checkForClassIsUsed(self, Class):
    current_set_of_classes = set(self.GRAPHS.keys())
    found = 0
    uri = self.makeURI("ROOT", Class)
    for c in current_set_of_classes:
      triple = (None, None, uri)
      for t in self.GRAPHS[c].triples(triple):
        found += 1

    if found == 0:
      dialog = makeMessageBox("remove class %s" % Class, buttons=["NO", "YES"])
      if dialog == "YES":
        self.removeClass(Class)

  def removeClass(self, Class):
    for c in self.getClassNamesList():
      classURI = self.makeURI(c, Class)
      graph = self.GRAPHS[c]
      triple = (None, RDFSTerms["is_defined_by"], classURI)
      for t in graph.triples(triple):
        graph.remove(t)
    del self.GRAPHS[Class]

    # self.removeAllLinksToClass(Class)
    return self.getClassNamesList()

  def addSubclass(self, Class, ClassOrSubClass, name):
    if Class == ClassOrSubClass:
      _, o = self.makeClassURI(Class)
    else:
      o = self.makeURI(Class, ClassOrSubClass)
    s = self.makeURI(Class, name)

    triple = (s, RDFSTerms["is_member"], o)
    self.addElucidation(Class, s)
    self.GRAPHS[Class].add(triple)
    pass

  def removeSubClass(self, Class, item):
    s = self.makeURI(Class, item)
    triple = s, RDFSTerms["is_member"], None
    for t in self.GRAPHS[Class].triples(triple):
      self.GRAPHS[Class].remove(t)
      pass

  def addPrimitive(self, Class, ClassOrSubClass, name, type):
    no = self.data_counters.incrementCounter(type)
    o = self.makeURI(Class, name + "-%s" % no)
    s = self.makeURI(Class, ClassOrSubClass)
    p = RDFSTerms["value"]
    triple = s, p, o
    self.GRAPHS[Class].add(triple)
    sv = o  # self.makeURI(Class, name)
    p = RDFSTerms["data_type"]
    ov = RDFSTerms[type]  # self.makeURI(Class, name) #s
    # triple = s,p,ov
    triple = sv, p, ov
    self.GRAPHS[Class].add(triple)

  # def addElucidation(self, elucidation, Class, name):
  #
  #   s = self.makeURI(Class, name)
  #   p = RDFSTerms["value"]
  #   o = self.makeURI(Class, "elucidation")
  #   triple = s, p, o
  #   self.GRAPHS[Class].add(triple)
  #   # p = RDFSTerms["data_type"]
  #   # ov = RDFSTerms["string"]
  #   # triple = s, p, ov    # self.GRAPHS[Class].add(triple)
  #   # p = "elucidation"
  #   oe = rdflib.term.Literal(elucidation, lang="en")
  #   # oe = Literal("Literal\elucidation", lang="en")
  #   triple = o, p, oe
  #   self.GRAPHS[Class].add(triple)

  def addLink(self, Class, obj, subj):
    subject = self.makeURI(Class, subj)
    object = self.makeURI(Class, obj)
    predicate = RDFSTerms["is_defined_by"]
    self.GRAPHS[Class].add((subject, predicate, object))

  def removeLinkInClass(self, Class, item):

    o_name = self.getLinkList(Class, item)[0]
    object = self.makeURI(Class, o_name)

    subject = self.makeURI("ROOT", item)
    triple = (subject, RDFSTerms["is_defined_by"], object)

    # triple = (None, RDFSTerms["is_defined_by"], object)
    for s, p, o in self.GRAPHS[Class].triples(triple):
      object = extract_name_from_class_uri(o)
    self.GRAPHS[Class].remove(triple)
    return object

  def removePrimitive(self, Class, primitive):
    graph = self.GRAPHS[Class]
    primitiveURI = self.makeURI(Class, primitive)
    for t in graph.triples((None, None, primitiveURI)):
      graph.remove(t)
    for t in graph.triples((primitiveURI, None, None)):
      graph.remove(t)
    pass

  def isRoot(self, name):
    return name == ROOTCLASS

  def isClass(self, name):
    l = self.getClassNamesList()
    return name in l

  def isSubClass(self, Class, name):
    l = self.getSubClassList(Class)
    return name in l

  def isLinkedWidth(self, Class, name):
    l = self.getLinkList(Class, name)
    return l != []

  def isPrimitive(self, Class, name):
    return name in PRIMITIVES

  def isInteger(self, Class, name):
    return name in self.getIntegerList(Class)

  def isString(self, Class, name):
    return name in self.getStringList(Class)

  def isElucidation(self, Class, name):
    # uri = self.makeURI(Class, name)
    return "elucidation" in name

  def isValue(self, Class, name):
    return name in self.getValueList(Class)

  def what_is_this(self, Class, name):
    what = []
    if self.isClass(name) or (name == "Class"): what.append("class")
    if self.isSubClass(Class, name): what.append("is_member")
    if self.isInteger(Class, name): what.append("integer")
    if self.isString(Class, name): what.append("string")
    if self.isValue(Class, name): what.append("value")
    if self.isElucidation(Class, name): what.append("elucidation")
    if self.isLinkedWidth(Class, name): what.append("linked")
    return what

class GUIMessage(dict):
  def __init__(self, event=None, name=None, type=None):
    self["event"] = event
    self["name"] = name
    self["type"] = type



class OntobuilderUI(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

    self.DEBUGG = True

    # roundButton(self.ui.pushLoad, "load", tooltip="load ontology")
    # roundButton(self.ui.pushCreate, "plus", tooltip="create")
    # roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    # roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    # # roundButton(self.ui.pushExit, "exit", tooltip="exit")
    # roundButton(self.ui.pushSaveAs, "save_as", tooltip="save with new name")
    # roundButton(self.ui.pushBricks, "bricks", tooltip="building bricks mode")
    # roundButton(self.ui.pushTree, "build_tree", tooltip="building tree mode")
    # roundButton(self.ui.pushInstantiate, "instantiate_tree", tooltip="instantiate tree mode")

    roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
    roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
    roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)
    # roundButton(self.ui.pushExit, "reject", tooltip="exit", mysize=35)

    self.gui_objects = {
            "ontology_control"      : self.ui.groupBoxOntology,
            "ontology_create"       : self.ui.pushOntologyCreate,
            "ontology_load"         : self.ui.pushOntologyLoad,
            "ontology_save"         : self.ui.pushOntologySave,
            "ontology_save_as"      : self.ui.pushOntologySaveAs,
            "tab_lists_control"     : self.ui.tabWidgetLists,
            # "tab_bricks"            : self.ui.tabWidgetLists.setCurrentIndex(0),
            # "tab_tree"              : self.ui.tabWidgetLists.setCurrentIndex(1),
            "brick_create"          : self.ui.pushBrickCreate,
            "brick_delete"          : self.ui.pushBrickRemove,
            "brick_add_item"        : self.ui.pushBrickAddItem,
            "brick_remove_item"     : self.ui.pushBrickRemoveItem,
            "brick_add_primitive"   : self.ui.pushBrickAddPrimitive,
            "brick_remove_primitive": self.ui.pushBrickRemovePrimitive,
            "brick_rename"          : self.ui.pushBrickRename,
            "brick_list"            : self.ui.listBricks,
            "tree_control"          : self.ui.groupBoxTree,
            "tree_create"           : self.ui.pushTreeCreate,
            "tree_delete"           : self.ui.pushDeleteTree,
            "tree_add_link"         : self.ui.pushTreeLinkExistingClass,
            "tree_remove_link"      : self.ui.pushTreeRemoveClassLink,
            "tree_instantiate"      : self.ui.pushTreeInstantiate,
            "tree_visualise"        : self.ui.pushTreeVisualise,
            "tree_select_brick"     : self.ui.comboBoxTreeSelectBrick,
            "tree"                  : self.ui.treeTree,
            "primitives_control"    : self.ui.groupBoxPrimitives,
            "primitives_line_edit"  : self.ui.linePrimitivesLineEdit,
            "primitives_combo_box"  : self.ui.comboBoxPrimitives,
            "primitives_text_edit"  : self.ui.textPrimitivesTextEdit,
            "minimise"              : self.ui.pushMinimise,
            "maximise"              : self.ui.pushMaximise,
            "normal"                : self.ui.pushNormal,
            "exit"                  : self.ui.pushExit,
            }
    # w = 150
    # h = 25
    # for i in ["add_subclass", "add_primitive", "link_new_class", "link_existing_class"]:
    #   self.gui_objects[i].setFixedSize(w, h)

    self.backend = BackEnd(self)

    message = GUIMessage(event="start")
    self.backend.processEvent(message)
    #
    # self.ontology_graph = None
    # self.ontology_root = None
    self.changed = False
    #
    # # self.__ui_state("start")
    # self.current_class = None
    # self.current_item_ID = None
    # self.class_path = []
    # self.elucidations = {}
    # self.selected_item = None
    # self.previously_selected_item = None
    # self.load_elucidation = True

  def setInterface(self,settings):
    for show in settings["show"]:
      self.gui_objects[show].show()
    for hide in settings["hide"]:
      self.gui_objects[hide].hide()

  def on_pushOntologyCreate_pressed(self):
    debugging("-- pushOntologyCreate")
    event = "create ontology"
    dialog = UI_String("provide new ontology name",placeholdertext="ontology name")
    dialog.exec()
    name = dialog.text
    message = GUIMessage(event=event, name=name)
    self.backend.processEvent(message)


  def on_pushOntologyLoad_pressed(self):
    debugging("-- ontology_load")
    file_spec, extension = QFileDialog.getOpenFileName(None,
                                         "Load Ontology",
                                         ONTOLOGY_REPOSITORY,
                                         "*.%s" % FILE_FORMAT,
                                         )
    if file_spec == "":
      return
    project_name = os.path.basename(file_spec).split(os.path.extsep)[0]
    message = GUIMessage(event="load ontology", name=project_name)
    self.backend.processEvent(message)

    # self.dataModel = DataModel()
    #
    # self.dataModel.loadFromFile(self.project_file_spec)
    # self.current_class = ROOTCLASS
    # self.__addToClassPath(ROOTCLASS)
    # self.__createTree(self.current_class)
    # self.__ui_state("show_tree")

  def on_pushOntologySave_pressed(self):
    debugging("-- pushOntologySave")

  def on_pushOntologySaveAs_pressed(self):
    debugging("-- pushOntologySaveAs")

  def on_pushBrickCreate_pressed(self):
    debugging("-- pushBrickCreate")

  def on_pushBrickRemove_pressed(self):
    debugging("--pushBrickRemove")

  def on_push_pushBrickAddItem_pressed(self):
    debugging("-- pushBrickAddItem")

  def on_pushBrickRemoveItem_pressed(self):
    debugging("-- pushBrickRemoveItem")

  def on_pushBrickAddPrimitive_pressed(self):
    debugging("-- pushBrickAddPrimitive")

  def on_pushBrickRemovePrimitive_pressed(self):
    debugging("-- pushBrickRemovePrimitive")

  def on_pushBrickRename_pressed(self):
    debugging("-- pushBrickRename")

  def on_pushTreeCreate_pressed(self):
    debugging("-- pushTreeCreate")

  def on_pushDeleteTree_pressed(self):
    debugging("-- pushDeleteTree")

  def on_pushTreeLinkExistingClass_pressed(self):
    debugging("-- pushTreeLinkExistingClass")

  def on_pushTreeRemoveClassLink_pressed(self):
    debugging("-- pushTreeRemoveClassLink")

  def on_pushTreeInstantiate_pressed(self):
    debugging("-- pushTreeInstantiate")

  def on_pushTreeVisualise_pressed(self):
    debugging("-- pushTreeVisualise")

  def on_pushMinimise_pressed(self):
    self.showMinimized()

  def on_pushMaximise_pressed(self):
    self.showMaximized()

  def on_pushNormal_pressed(self):
    self.showNormal()


  def on_tabWidgetLists_currentChanged(self, index):
    debugging("-- tabWidgetLists -- index", index)

  def on_listBricks_itemClicked(self, item):
    name = item.text()
    debugging("-- listBricks -- item", name)

  def on_treeTree_itemClicked(self, item, column):
    name = item.text()
    debugging("-- tree item %s, column %s"%(name,column))



  def __ui_state(self, state):
    # what to show
    if state == "start":
      show = ["load",
              "create",
              "exit",
              ]
    elif state == "show_tree":
      show = ["save",
              "save_as",
              "exit",
              "visualise",
              ]
    elif state == "selected_subclass":
      show = ["save",
              "save_as",
              "exit",
              "add_subclass",
              "add_primitive",
              "link_new_class",
              "link_existing_class",
              "remove_subclass",
              "elucidation",
              ]
    elif state == "selected_root":
      show = ["save",
              "save_as",
              "exit",
              "add_subclass",
              "add_primitive",
              "elucidation",
              ]
    elif state == "selected_class":
      show = ["save",
              "save_as",
              "exit",
              "add_subclass",
              "add_primitive",
              "elucidation",
              "remove_class",
              ]
    elif state == "selected_primitive":
      show = ["save",
              "save_as",
              "exit",
              ]
    elif state == "selected_value":
      show = ["save",
              "save_as",
              "exit",
              "elucidation",
              "remove_primitive"
              ]
    elif state == "no_existing_classes":
      show = ["save",
              "save_as",
              "exit",
              "add_subclass",
              "add_primitive",
              "link_new_class",
              "elucidation",
              ]
    elif state == "is_linked":
      show = ["save",
              "save_as",
              "exit",
              "add_primitive",
              "elucidation",
              "remove_class_link",
              ]
    else:
      show = []

    for b in self.gui_objects:
      if b not in show:
        self.gui_objects[b].hide()
      else:
        self.gui_objects[b].show()

  def debugging(self, *info):
    if self.DEBUGG:
      print("debugging", info)

  def on_pushCreate_pressed(self):
    dialog = UI_String("name for your ontology file",
                       placeholdertext="file name extension is default")
    dialog.exec()
    name = dialog.getText()
    self.project_name = name
    if name:
      self.project_file_spec = os.path.join(ONTOLOGY_REPOSITORY, name + ".%s" % FILE_FORMAT)
    else:
      return

    self.dataModel = DataModel()
    self.current_class = ROOTCLASS
    self.class_path = [ROOTCLASS]
    self.ui.listClasses.addItems(self.class_path)  # make class list
    self.changed = True

    self.__createTree(ROOTCLASS)

  def on_textElucidation_textChanged(self):
    print("debugging change text", self.ui.textElucidation.toPlainText())
    # self.current_class
    # self.current_item_ID

    self.ui.pushAddElucidation.show()

  def on_pushAddElucidation_pressed(self):  # TODO: fix
    elucidation = self.ui.textElucidation.toPlainText()
    print("not implemented")
    # print("debugging elucidations", elucidation)
    # self.dataModel.addElucidation(elucidation, self.current_class, self.current_item_ID)
    pass

    # self.load_elucidation = True
    # self.ui.pushAddElucidation.hide()
    # text_ID = self.selected_item.text(0)
    # predicate = self.selected_item.predicate
    # if self.__hasElucidation(text_ID, predicate):
    #   p = self.__makePathName(text_ID)
    #   d = self.ui.textElucidation.toPlainText()
    #   self.elucidations[p] = d
    #   pass

  def on_treeClass_itemPressed(self, item, column):

    button = QApplication.instance().mouseButtons().name
    text_ID = item.text(column)
    if button == "RightButton":
      # print("right button pressed")
      if ELUCIDATION in text_ID:
        makeMessageBox("cannot be renamed ", buttons=["OK"])
        return
      ID = str(text_ID)
      is_subclass = self.dataModel.isSubClass(self.current_class, ID)
      is_value = self.dataModel.isValue(self.current_class, ID)
      if (is_subclass or is_value):
        prompt = "new name"
        placeholder = str(item.text(0))

        new_name = self.__getConstraintString(placeholder, prompt)
        if new_name:
          self.__renameItemInGraph(ID, new_name)
      return
    elif button == "MiddleButton":
      print("middle button pressed -- no action")
      return

    else:  # button == "LeftButton":
      # print("left button pressed")
      pass

    self.current_item_ID = text_ID

    debugging("you picked column %s with id %s" % (column, text_ID),
                   self.dataModel.what_is_this(self.current_class, text_ID))

    try:
      predicate = item.predicate
    except:
      print(">>>>>>>>>>>>>>>>> no predicate")
      item.predicate = None
      predicate = None
    self.selected_item = item
    debugging("column ", column)

    item.setSelected(True)  # sets background

    if self.previously_selected_item:  # TODO: needed?
      debugging("column ", self.previously_selected_item.columnCount())
      # self.previously_selected_item.setBackground(column, QBRUSHES["unselect"])
      self.previously_selected_item = self.selected_item

    # if text_ID in self.class_names:
    is_root = self.dataModel.isRoot(text_ID)
    isclass = self.dataModel.isClass(text_ID)
    is_linked_with = self.dataModel.isLinkedWidth(self.current_class, text_ID)
    is_item = self.dataModel.isSubClass(self.current_class, text_ID)
    is_primitive = self.dataModel.isPrimitive(self.current_class, text_ID)
    is_value = self.dataModel.isValue(self.current_class, text_ID)
    is_elucidation = self.dataModel.isElucidation(self.current_class, text_ID)
    is_comment = text_ID == "comment"

    if isclass:  # set gui state
      debugging("-- is class", text_ID)
      self.__ui_state("selected_class")
      if self.current_class != text_ID:
        self.__shiftClass(text_ID)
      if is_root:
        debugging("-- is root", text_ID)
        self.__ui_state("selected_root")
    elif is_linked_with:
      debugging("-- is linked", text_ID)
      self.__ui_state("is_linked")
    elif is_item:
      debugging("-- it is a subclass", text_ID)
      self.__ui_state("selected_subclass")
    elif is_primitive:
      debugging("-- is a primitive", predicate)
      self.__ui_state("selected_primitive")
    elif is_value:
      self.__ui_state("selected_value")
      debugging("-- isvalue", predicate)
    elif is_elucidation:
      pass
    else:
      print("should not come here")
      self.__ui_state("show_tree")

    # if self.dataModel.getElucidationList(self.current_class):
    #   self.ui.pushAddElucidation.hide()
    #   self.load_elucidation = True
    #   p = self.__makePathName(text_ID)
    #   not_exist = None
    #   try:
    #     self.ui.textElucidation.setPlainText(self.elucidations[p])
    #   except:
    #     not_exist = p
    #     self.ui.textElucidation.clear()
    #
    #   if not_exist:
    #     self.elucidations[not_exist] = ""

    self.ui.treeClass.clearSelection()

  def on_pushAddSubclass_pressed(self):
    # print("debugging -- add subclass")

    # get an identifier for the subclass
    prompt = "name for subclass"
    subClass = self.__getConstraintString(prompt)

    if not subClass:
      return

    # elucidation
    p = self.__makePathName(subClass)  # TODO add elucidation handling
    # self.elucidations[p] = None
    # self.ui.textElucidation.clear()

    # add to graph
    self.dataModel.addSubclass(self.current_class, self.current_item_ID, subClass)

    # generate GUI tree
    self.__createTree(self.current_class)
    self.changed = True

  def on_pushRemoveSubClass_pressed(self):
    pass
    itemID = self.current_item_ID
    Class = self.current_class
    self.dataModel.removeSubClass(Class, itemID)
    self.__createTree(self.current_class)
    self.changed = True

  def on_pushAddPrimitive_pressed(self):
    debugging("add primitive first")
    # forbidden = self.subclass_names[self.current_class]

    prompt = "name for primitive"
    primitive_ID = self.__getConstraintString(prompt)
    debugging("debugging -- ", primitive_ID)
    if not primitive_ID:
      return

    permitted_classes = PRIMITIVES
    dialog2 = UI_stringSelector("choose primitive", permitted_classes)
    dialog2.exec()

    primitive_class = dialog2.getSelection()
    if not primitive_class:
      return
    debugging("add primitive")
    self.dataModel.addPrimitive(self.current_class, self.current_item_ID, primitive_ID, primitive_class)
    debugging("end of add")
    self.__createTree(self.current_class)
    self.changed = True

  def on_pushAddNewClass_pressed(self):
    # print("debugging -- add class")

    prompt = "name for subclass"
    Class = self.__getConstraintString(prompt)
    if not Class:
      return

    newClass = Class.upper()

    self.dataModel.addClass(newClass)

    # elucidation
    self.ui.textElucidation.clear()
    self.elucidations[Class] = None

    # make link
    self.dataModel.addLink(self.current_class, newClass, self.current_item_ID)

    self.__createTree(newClass)
    self.__addToClassPath(addclass=newClass)
    self.current_class = newClass
    self.__ui_state("show_tree")
    self.changed = True

  def on_pushAddExistingClass_pressed(self):
    permitted_classes = self.__permittedClasses()

    # permitted_classes
    if permitted_classes:
      dialog = UI_stringSelector("select", permitted_classes)
      dialog.exec()
      selection = dialog.getSelection()
      if not selection:
        return

      Class = selection
      _, object = self.dataModel.makeClassURI(Class)
      subject = self.dataModel.makeURI(self.current_class, self.current_item_ID)
      triple = (subject, RDFSTerms["is_defined_by"], object)
      self.dataModel.GRAPHS[self.current_class].add(triple)
      print("adding triple:", triple)

      parent_item = self.ui.treeClass.currentItem()
      item = QTreeWidgetItem(parent_item)
      item.setText(0, Class)
      p = "is_defined_by"
      item.predicate = p
      # item.setBackground(0, LINK_COLOUR)
      item.setForeground(0, QBRUSHES[p])
      self.ui.treeClass.expandAll()
      self.changed = True

  def on_pushRemoveClass_pressed(self):

    item = self.selected_item
    Class = item.text(0)
    self.dataModel.removeClass(Class)

    self.class_path.remove(Class)
    previous_class = self.class_path[-1]
    self.current_class = previous_class
    self.__shiftClass(previous_class)
    self.changed = True

  def on_pushRemoveClassLink_pressed(self):

    removed_class = self.dataModel.removeLinkInClass(self.current_class, self.current_item_ID)
    # self.__checkForUnusedClasses(removed_class)
    self.dataModel.checkForClassIsUsed((removed_class))
    self.__createTree(self.current_class)
    self.__ui_state("show_tree")
    self.changed = True

  def on_pushSave_pressed(self):
    # print("debugging -- pushSave")

    conjunctiveGraph = self.__prepareConjunctiveGraph()
    self.__writeQuadFile(conjunctiveGraph, self.project_file_spec)

    project_file_spec_json = os.path.join(ONTOLOGY_REPOSITORY, self.project_name + ".%s" % FILE_FORMAT_)

    self.__writeQuadFile(conjunctiveGraph, project_file_spec_json)

    self.changed = False

  def on_pushRemovePrimitive_pressed(self):
    self.dataModel.removePrimitive(self.current_class, self.current_item_ID)

    self.__createTree(self.current_class)
    self.__ui_state("show_tree")

    self.change = True

  def on_pushSaveAs_pressed(self):

    conjunctiveGraph = self.__prepareConjunctiveGraph()

    dialog = QFileDialog.getOpenFileName(None,
                                         "save Ontology as",
                                         ONTOLOGY_REPOSITORY,
                                         "*.%s" % FILE_FORMAT,
                                         )
    file_name = dialog[0]
    if not file_name:
      file_names = []
      for file in glob.glob("%s/*.%s" % (ONTOLOGY_REPOSITORY, FILE_FORMAT)):
        basename = os.path.basename(file)
        name, _ = basename.split(".")
        file_names.append(name)

      dialog = UI_String("name for subclass", limiting_list=file_names)
      dialog.exec()
      file_name = dialog.getText()
      if not file_name:
        return
    else:
      file_name = file_name.split(".")[0]

    for f_format in [FILE_FORMAT, FILE_FORMAT_]:
      fname = file_name + ".%s" % f_format
      self.project_file_spec = os.path.join(ONTOLOGY_REPOSITORY, fname)
      self.__writeQuadFile(conjunctiveGraph, self.project_file_spec)

    dot = self.__makeDotGraph()

    self.changed = False

  def on_pushLoad_pressed(self):
    dialog = QFileDialog.getOpenFileName(None,
                                         "Load Ontology",
                                         ONTOLOGY_REPOSITORY,
                                         "*.%s" % FILE_FORMAT,
                                         )
    self.project_file_spec = dialog[0]
    self.project_name = os.path.basename(self.project_file_spec).split(os.path.extsep)[0]
    if dialog[0] == "":
      return

    self.dataModel = DataModel()

    self.dataModel.loadFromFile(self.project_file_spec)
    self.current_class = ROOTCLASS
    self.__addToClassPath(ROOTCLASS)
    self.__createTree(self.current_class)
    self.__ui_state("show_tree")

  def on_listClasses_itemClicked(self, item):
    Class = item.text()
    self.__shiftClass(Class)

  def on_pushVisualise_pressed(self):

    dot = self.__makeDotGraph()

  def on_pushExit_pressed(self):
    self.closeMe()

  def closeEvent(self, event):
    self.closeMe()

  def closeMe(self):
    if self.changed:
      # dialog = QMessageBox()
      dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
      if dialog == "YES":
        # print("save")
        self.on_pushSave_pressed()

      elif dialog == "NO":
        pass
        # print("exit")
    else:
      pass
      # print("no changes")
    sys.exit()

  def __createTree(self, origin):
    widget = self.ui.treeClass
    widget.clear()

    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = origin
    rootItem.setText(0, origin)
    rootItem.setSelected(False)
    rootItem.predicate = None
    widget.addTopLevelItem(rootItem)
    self.current_class = origin
    tuples = self.__prepareTree(origin)
    self.__makeTree(tuples, origin=origin, stack=[], items={origin: rootItem})
    widget.show()
    widget.expandAll()
    self.__ui_state("show_tree")

  def __prepareTree(self, origin):
    graph = self.dataModel.GRAPHS[origin]  # self.current_class]
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

      if predicate in [RDFSTerms["is_defined_by"], RDFSTerms["value"], RDFSTerms["data_type"]]:
        triple = o, p, s, -1
      else:
        triple = s, p, o, 1

      tuples_plus.append(triple)

    debugging("tuples", tuples_plus)

    return tuples_plus

  def __prepareConjunctiveGraph(self):
    conjunctiveGraph = ConjunctiveGraph("Memory")
    namespaces = self.dataModel.namespaces
    for ns in namespaces:
      conjunctiveGraph.bind(ns, namespaces[ns])
    for cl in self.dataModel.getClassNamesList():  # class_definition_sequence:
      for s, p, o in self.dataModel.GRAPHS[cl].triples((None, None, None)):
        # print(s, p, o)
        conjunctiveGraph.get_context(namespaces[cl]).add((s, p, o))
    return conjunctiveGraph

  # def __checkForUnusedClasses(self, ):
  #
  #   unused_classes = set(self.dataModel.GRAPHS.keys())
  #   current_set_of_classes = copy.copy(unused_classes)
  #
  #   for c in current_set_of_classes:
  #     uri = self.dataModel.makeURI("ROOT",c)
  #     for t in self.dataModel
  #
  #
  #   # current_set_of_classes = set(self.dataModel.GRAPHS.keys())
  #   # used_classes_set = set([])
  #   # for c in current_set_of_classes:
  #   #   if c not in removed_class:
  #   #     for s, p, o in self.dataModel.GRAPHS[c].triples((None, None, None)):
  #   #       t1 =(extract_class_name(s) in current_set_of_classes)
  #   #       t2 = (extract_name_from_class_uri(o) in current_set_of_classes)
  #   #       if t1 or t2:
  #   #         used_classes_set.add(c)
  #   # # not used classes:
  #   # not_used_classes = current_set_of_classes - used_classes_set
  #   # debugging("not used set of classes: ", not_used_classes)
  #   #
  #   # to_remove_classes = set()
  #
  #   not_used_classes = not_used_classes
  #   for c in not_used_classes:
  #     untreated_classes = not_used_classes - to_remove_classes - set("ROOT")
  #     dialog = UI_stringSelector("you got unused classes -- select the one you want to delete or cancel",
  #                                untreated_classes)
  #     dialog.exec()
  #     selection = dialog.getSelection()
  #     if selection:
  #       self.dataModel.removeClass(selection)
  #       untreated_classes.remove(selection)
  #     else:
  #       break

  def __writeQuadFile(self, conjunctiveGraph, f):
    saveBackupFile(f)
    inf = open(f, "w")
    inf.write(conjunctiveGraph.serialize(format=FILE_FORMAT))
    inf.close()
    print("written to file ", f)

  def __makeTree(self, tuples, origin=[], stack=[], items={}):
    for q in tuples:
      if q not in stack:
        s, p, o, dir = q
        if s != origin:
          if o in items:
            item = QTreeWidgetItem(items[o])
            item.identifier = o
            item.predicate = p
            item.setForeground(0, QBRUSHES[p])
            stack.append(q)  # (s, p, o))
            item.setText(0, s)
            items[s] = item
            self.__makeTree(tuples, origin=s, stack=stack, items=items)

  def __renameItemInGraph(self, ID, new_name):
    graph = self.dataModel.GRAPHS[self.current_class]
    makeURI__ = self.dataModel.makeURI
    old_ID = makeURI__(self.current_class, ID)
    new_ID = makeURI__(self.current_class, new_name)
    for s, p, o in graph.triples((None, None, old_ID)):
      # print("debugging -- change triple", s, p, o)
      self.dataModel.GRAPHS[self.current_class].remove((s, p, o))
      object = new_ID
      self.dataModel.GRAPHS[self.current_class].add((s, p, object))
    for s, p, o in graph.triples((old_ID, None, None)):
      # print("debugging -- change triple", s, p, o)  # add to graph
      self.dataModel.GRAPHS[self.current_class].remove((s, p, o))
      subject = new_ID
      self.dataModel.GRAPHS[self.current_class].add((subject, p, o))
    self.__createTree(self.current_class)
    self.__ui_state("show_tree")

  def __makePathName(self, text_ID):  # todo: to remove
    p = ROOTCLASS
    for i in self.class_path[1:]:
      p = p + ".%s" % i
    if text_ID not in p:
      item_name = text_ID
      p = p + ".%s" % item_name
    return p

  def __hasElucidation(self, text_ID, predicate):
    return self.__isClass(text_ID) or self.__isSubClass(text_ID) or self.__isValue(predicate)

  def __addItemToTree(self, internal_object, predicate, internal_subject, parent_item=None):
    # generate GUI tree
    if not parent_item:
      parent_item = self.ui.treeClass.currentItem()
    item = QTreeWidgetItem(parent_item)
    item.setText(0, internal_object)
    item.predicate = predicate
    # item.setBackground(0, COLOURS[predicate])# PRIMITIVE_COLOUR)
    item.setForeground(0, QBRUSHES[predicate])
    self.ui.treeClass.expandAll()
    self.changed = True
    return item

  def __permittedClasses(self):
    all_linked_classes = self.dataModel.getAllLinkedClasses()
    permitted_classes = copy.copy(all_linked_classes)
    for c in all_linked_classes:
      if (c == self.current_class) or (c in self.class_path):
        permitted_classes.remove(c)

    return permitted_classes

  def __addToClassPath(self, addclass):
    self.class_path.append(addclass)
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

  def __removeClassPath(self, Class):
    class_path = []
    for c in self.class_path:
      if Class != c:
        class_path.append(c)
    self.class_path = class_path
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

  def __cutClassPath(self, cutclass):
    i = self.class_path.index(cutclass)
    self.class_path = self.class_path[:i + 1]
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

  def __shiftClass(self, Class):
    # print("debugging ---------------")
    self.current_class = Class
    self.__createTree(Class)
    if Class not in self.class_path:
      self.__addToClassPath(Class)
    else:
      self.__cutClassPath(Class)
    self.__ui_state("show_tree")

  def __getConstraintString(self, prompt, placeholder=""):
    forbidden = self.dataModel.getAllNames(self.current_class)
    dialog = UI_String(prompt, placeholdertext=placeholder, limiting_list=forbidden)
    dialog.exec()
    return dialog.getText()

  def __makeDotGraph(self):
    class_names = self.dataModel.getClassNamesList()
    triples = set()
    for Class in class_names:
      for t in self.__prepareTree(Class):
        triples.add(t)
    pass
    print("\n---------------------------------")
    file_name = os.path.join(ONTOLOGY_REPOSITORY, self.project_name)
    dot = TreePlot(file_name, triples, class_names)
    for s, p, o, dir in triples:
      debugging("adding node", s, p, o)
      subject_type = self.dataModel.what_is_this(self.current_class, s)
      object_type = self.dataModel.what_is_this(self.current_class, o)

      # type = "other"
      try:
        type = object_type[0]
      except:
        type = "other"

      # print("s,p,o is:", s, ": ", subject_type,
      #       "p: ", p,
      #       "o: ", o, object_type,
      #       "d: ", dir)
      print("s: ", s, subject_type, "      p:", p, "     o: ", o, object_type, "     dir:", dir)
      if "class" in object_type:
        type = "Class"
      if "linked" in object_type:
        type = "linked"
      if o == "Class":
        type = "Class"

      if dir == -1:
        node = s
        if "class" in subject_type:
          type = "Class"
        if s in PRIMITIVES:
          type = "primitive"
        elif not subject_type:
          type = "other"
      else:
        if "class" in object_type:
          type = "Class"
        node = o

      # print(node)
      # print("adding", node, type)

      dot.addNode(node, type)

    for s, p, o, dir in triples:
      if dir == -1:
        dot.addEdge(o, s, p)
      else:
        dot.addEdge(s, o, p)
    pass
    # dot.dot.view()
    file_path = os.path.join(ONTOLOGY_REPOSITORY, self.project_name + "pdf")
    ggg = dot.dot.render(view=True, cleanup=True)
    # os.rename(ggg, file_path)

    return

  # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s
  def mousePressEvent(self, event, QMouseEvent=None):
    self.dragPos = event.globalPosition().toPoint()

  def mouseMoveEvent(self, event, QMouseEvent=None):
    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
    self.dragPos = event.globalPosition().toPoint()


class BackEnd():
  def __init__(self,frontEnd):
    self.state = "start"
    self.UI_state = {
            "start": {
                    "show": ["ontology_control",
                             "ontology_load",
                             "ontology_create"],
                    "hide": ["ontology_save",
                             "ontology_save_as",
                             "tab_lists_control",
                             "tree_control",
                             "primitives_control",
                             ],
                    },
            "create ontology": {
                    "show": [],
                    "hide": [],
                    },
            "load ontology": {
                    "show": [],
                    "hide": [],
                    },
            }
    self.actions = {
            "start" : [],
            "create ontology": ["createOntology"],
            "load ontology": [],
            }
    pass

    self.frontEnd = frontEnd
    self.dataModel = DataModel("root")

  def processEvent(self, message):
    event = message["event"]
    ui_state = self.UI_state[event]
    self.frontEnd.setInterface(ui_state)
    for a in self.actions[event]:
      c = "self.%s(message)"%a
      exec(c)

  def createOntology(self, message):
    debugging("> action", message)
    pass



if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = OntobuilderUI()
  MainWindow.show()
  sys.exit(app.exec())
