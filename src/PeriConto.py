#!/usr/local/bin/python3

"""
This version uses RDF syntax for the predicates. The subjects and objects are Literals. The latter caused problems
when saving using the serializers. It can be saved but not read afterwards.

So the approach is to use an internal representation of the predicates and translate when loading and saving.


"""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


import glob
import os
import sys

from rdflib import Namespace

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, 'resources')])

from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *
from graphviz import Digraph
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import URIRef
from rdflib import XSD
from rdflib import namespace
# from rdflib.namespace import RDFS

# from graphHAP import Graph
from PeriConto_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String
from resources.ui_single_list_selector_impl import UI_stringSelector

# https://www.w3.org/TR/rdf12-concepts/#dfn-rdf-dataset
# https://www.w3.org/TR/rdf-schema/#ch_resource

RDFS = namespace.RDFS
BASE = "http://example.org"
CLASS_SEPERATOR = "#"
PERICONTO = BASE + CLASS_SEPERATOR

ONTOLOGY_REPOSITORY = "../ontologyRepository"
ROOTCLASS = "root"

FILE_FORMAT = "trig"

RDFSTerms = {
        "class"           : RDFS.Class,
        "is_type"         : RDF.type,
        "is_a_subclass_of": RDFS.subClassOf,
        "link_to_class"   : RDFS.isDefinedBy,
        "value"           : RDF.value,
        "comment"         : RDFS.comment,
        "integer"         : XSD.integer,
        "string"          : XSD.string,
        "type"            : RDF.type,
        }

MYTerms = {v: k for k, v in RDFSTerms.items()}

PRIMITIVES = ["integer", "string", "comment"]
ADD_ELUCIDATIONS = ["class", "subclass", "value"]

COLOURS = {
        "is_a_subclass_of": QtGui.QColor(0, 0, 0, 255),
        "link_to_class"   : QtGui.QColor(255, 100, 5, 255),
        "value"           : QtGui.QColor(155, 155, 255),
        "comment"         : QtGui.QColor(155, 155, 255),
        "integer"         : QtGui.QColor(155, 155, 255),
        "string"          : QtGui.QColor(255, 200, 200, 255),
        "selected"        : QtGui.QColor(252, 248, 192, 255),
        "unselect"        : QtGui.QColor(255, 255, 255, 255),
        }

EDGE_COLOUR = {
        "is_a_subclass_of": "blue",
        "link_to_class"   : "red",
        "value"           : "black",
        "comment"         : "green",
        "integer"         : "darkorange",
        "string"          : "cyan",
        }

QBRUSHES = {
        "is_a_subclass_of": QtGui.QBrush(COLOURS["is_a_subclass_of"]),
        "link_to_class"   : QtGui.QBrush(COLOURS["link_to_class"]),
        "value"           : QtGui.QBrush(COLOURS["value"]),
        "comment"         : QtGui.QBrush(COLOURS["comment"]),
        "integer"         : QtGui.QBrush(COLOURS["integer"]),
        "string"          : QtGui.QBrush(COLOURS["string"]),
        # "selected"        : QtGui.QBrush(COLOURS["selected"]), # not needed auto-implemented
        # "unselect"        : QtGui.QBrush(COLOURS["unselect"]),
        }

DIRECTION = {
        "is_a_subclass_of": 1,
        "link_to_class"   : 1,
        "value"           : -1,
        "comment"         : -1,
        "integer"         : -1,
        "string"          : -1,
        }

LINK_COLOUR = QtGui.QColor(255, 100, 5, 255)
PRIMITIVE_COLOUR = QtGui.QColor(255, 3, 23, 255)


def extractNameFromClassURI(uri):
  return uri.split(CLASS_SEPERATOR)[-1]


def plot(graph, class_names=[]):
  """
  Create Digraph plot
  """
  dot = Digraph()
  # Add nodes 1 and 2
  for s, p, o in graph.triples((None, None, None)):
    ss = str(s)
    ss_ = str(ss).replace(":", "-")
    sp = str(p)
    so = str(o)
    so_ = str(o).replace(":", "-")
    if ss in class_names:
      dot.node(ss_, color='red', shape="rectangle")
    elif so in PRIMITIVES:
      dot.node(so_, color='green', style='filled', fillcolor="gray", shape="none")
      # dot.node(so_, color='green', shape="rectangle")
    else:
      dot.node(ss_)

    if so == class_names[0]:
      dot.node(so_, style="filled", fillcolor="red", shape="none")
    elif so in class_names:
      dot.node(so_, style="filled", fillcolor="lightcoral", shape="none")
    else:
      dot.node(so_)

    my_p = MYTerms[p]

    if DIRECTION[my_p] == 1:
      dot.edge(ss_, so_,
               # label=my_p,
               color=EDGE_COLOUR[my_p])
    else:
      dot.edge(ss_, so_,
               # label=my_p,
               color=EDGE_COLOUR[my_p])

  # Visualize the graph
  return dot


#
#
# def putData(data, file_spec, indent="  "): #  NOTE: leave for the time beeing
#   print("writing to file: ", file_spec)
#   dump = json.dumps(data, indent=indent)
#   with open(file_spec, "w+") as f:
#     f.write(dump)


def getFilesAndVersions(abs_name, ext):
  base_name = os.path.basename(abs_name)
  ver = 0  # initial last version
  _s = []
  directory = os.path.dirname(abs_name)  # listdir(os.getcwd())
  files = os.listdir(directory)

  for f in files:
    n, e = os.path.splitext(f)
    #        print 'name', n
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


# def saveWithBackup(data, path): #  NOTE: leave for the time beeing
#   if os.path.exists(path):
#     old_path, new_path, next_path = saveBackupFile(path)
#   putData(data, path)
#
#
# def getData(file_spec):#  NOTE: leave for the time beeing
#   # print("get data from ", file_spec)
#   if os.path.exists(file_spec):
#     f = open(file_spec, "r")
#     data = json.loads(f.read())
#     return data
#   else:
#     return None


def makeRDFCompatible(identifier):  # TODO remove
  """
  To be adapted to imported notation.
  For now it generates rdflib Literals
  """
  return Literal(identifier)


class DataModel():
  def __init__(self):
    self.namespaces = {ROOTCLASS: Namespace(PERICONTO)}

    self.GRAPHS = {}
    self.addClass(ROOTCLASS)

  def __makeURIForClass(self, name):
    return URIRef(PERICONTO + name)

  def makeURI(self, Class, identifier):
    try:
      uri = URIRef(self.namespaces[Class] + "#" + identifier)
    except:
      pass
    # print("uri: ", identifier, "-->", uri)
    return uri

  def loadFromFile(self, file_name):
    data = ConjunctiveGraph("Memory")
    data.parse(file_name, format=FILE_FORMAT)

    self.GRAPHS = {}
    for i in data.contexts():
      Class = str(i.identifier).split("/")[-1]
      self.GRAPHS[Class] = data.get_graph(i.identifier)

    self.namespaces = {}
    for (prefix, namespace) in data.namespaces():
      self.namespaces[prefix] = namespace

  def getClassNamesList(self):
    return list(self.GRAPHS.keys())

  def getSubClassList(self, Class):
    triple = (None, RDFSTerms["is_a_subclass_of"], None)
    return [s for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getLinkList(self, Class):
    triple = (None, RDFSTerms["link_to_class"], None)
    return [o for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getIntegerList(self, Class):
    triple = (None, RDFSTerms["integer"], None)
    return [o for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getStringList(self, Class):
    triple = (None, RDFSTerms["string"], None)
    return [s for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getValueList(self, Class):
    triple = (None, RDFSTerms["value"], None)
    return [s for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getElucidationList(self, Class):
    triple = (None, RDFSTerms["comment"], None)
    return [s for s, p, o in self.GRAPHS[Class].triples(triple)]

  def getAllNames(self, Class):
    triple = (None, None, None)
    return [extractNameFromClassURI(s) for s, p, o in self.GRAPHS[Class].triples(triple)]
    # return [str(s).split(":")[-1] for c in self.GRAPHS for s,p,o in self.GRAPHS[c].triples(triple)]

  def addClass(self, Class):
    uid = '%s/%s' % (BASE, Class)
    uris = URIRef(uid)
    self.namespaces[Class] = Namespace(uid)
    self.GRAPHS[Class] = Graph("Memory", uris)  # uid)
    self.GRAPHS[Class].bind(Class, self.namespaces[Class])

    sub = URIRef(uid)
    triple = (sub, RDFSTerms["is_type"], RDFSTerms["class"])
    self.GRAPHS[Class].add(triple)
    return self.getClassNamesList()

  def removeClass(self, Class):
    del self.GRAPHS[Class]
    self.removeAllLinksToClass(Class)
    return self.getClassNamesList()

  def addSubclass(self, Class, ClassOrSubClass, name):
    s = self.makeURI(Class, name)
    o = self.makeURI(Class, ClassOrSubClass)
    triple = (s, RDFSTerms["is_a_subclass_of"], o)
    self.GRAPHS[Class].add(triple)
    pass

  def addLink(self, Class, subj, obj):
    subject = self.makeURI(Class, subj)
    object = self.makeURI(Class, obj)
    predicate = RDFSTerms["link_to_class"]
    self.GRAPHS[Class].add((subject, predicate, object))

  def removeAllLinksToClass(self, Class):
    for Class in self.getClassNamesList():
      subject = self.makeURI(Class, Class)
      triple = (subject, RDFSTerms["link_to_class"], None)
      for t in self.GRAPHS[Class].triples(triple):
        self.GRAPHS[Class].remove(t)

  def removeLinkInClass(self, Class, subClass):
    object = self.makeURI(Class, subClass)
    triple = (None, RDFSTerms["link_to_class"], object)
    for s, p, o in self.GRAPHS[Class].triples(triple):
      subject = extractNameFromClassURI(s)
    self.GRAPHS[Class].remove(triple)
    return subject

  def isRoot(self, name):
    return name == ROOTCLASS

  def isClass(self, name):
    l = self.getClassNamesList()
    return name in l

  def isSubClass(self, Class, name):
    l = self.getSubClassList(Class)
    return self.makeURI(Class, name) in l

  def isLinkedWidth(self, Class, name):
    return self.makeURI(Class, name) in self.getLinkList(Class)

  def isPrimitive(self, Class, name):
    return (self.isInteger(Class, name)
            or self.isString(Class, name)
            or self.isElucidation(Class, name)
            )

  def isInteger(self, Class, name):
    uri = self.makeURI(Class, name)
    return uri in self.getIntegerList(Class)

  def isString(self, Class, name):
    uri = self.makeURI(Class, name)
    return uri in self.getStringList(Class)

  def isElucidation(self, Class, name):
    uri = self.makeURI(Class, name)
    return (uri in self.getElucidationList(Class))

  def isValue(self, Class, name):
    uri = self.makeURI(Class, name)
    return (uri in self.getValueList(Class))

  def whatIsThis(self, Class, name):
    if self.isInteger(Class, name): return "integer"
    if self.isString(Class, name): return "string"
    if self.isValue(Class, name): return "value"
    if self.isClass(Class): return "class"
    if self.isSubClass(Class, name): return "subclass"
    if self.isElucidation(Class, name): return "elucidation"
    if self.isLinkedWidth(Class, name): return "linked"
    return None


class OntobuilderUI(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)  # ???

    self.DEBUGG = True

    roundButton(self.ui.pushLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushCreate, "plus", tooltip="create")
    roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")
    roundButton(self.ui.pushSaveAs, "save_as", tooltip="save with new name")

    self.gui_objects = {
            "load"               : self.ui.pushLoad,
            "create"             : self.ui.pushCreate,
            "visualise"          : self.ui.pushVisualise,
            "save"               : self.ui.pushSave,
            "save_as"            : self.ui.pushSaveAs,
            "exit"               : self.ui.pushExit,
            "add_subclass"       : self.ui.pushAddSubclass,
            "add_primitive"      : self.ui.pushAddPrimitive,
            "link_new_class"     : self.ui.pushAddNewClass,
            "link_existing_class": self.ui.pushAddExistingClass,
            "remove_subclass"    : self.ui.pushRemoveSubClass,
            "remove_primitive"   : self.ui.pushRemovePrimitive,
            "remove_class_link"  : self.ui.pushRemoveClassLink,
            "remove_class"       : self.ui.pushRemoveClass,
            "elucidation"        : self.ui.groupElucidation,
            "elucidation_button" : self.ui.pushAddElucidation,
            }
    w = 150
    h = 25
    for i in ["add_subclass", "add_primitive", "link_new_class", "link_existing_class"]:
      self.gui_objects[i].setFixedSize(w, h)

    self.ontology_graph = None
    self.ontology_root = None
    self.changed = False

    self.__ui_state("start")
    self.current_class = None
    self.current_class_or_subclass = None
    self.class_path = []
    self.elucidations = {}
    self.selected_item = None
    self.previously_selected_item = None
    self.load_elucidation = True

    self.CoatingOntology = Graph()
    # print("debugging -- read coating ontology")

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
              "remove_primitive"
              ]
    elif state == "value_selected":
      show = ["save",
              "save_as",
              "exit",
              "elucidation",
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
    if name:
      self.project_file_name = name + ".%s" % FILE_FORMAT
    else:
      self.close()
      return

    self.dataModel = DataModel()
    self.current_class = ROOTCLASS
    self.class_path = [ROOTCLASS]
    self.ui.listClasses.addItems(self.class_path)  # make class list
    self.changed = True

    self.__createTree(ROOTCLASS)

  def on_textElucidation_textChanged(self):
    # print("debugging change text")
    if self.load_elucidation:
      self.load_elucidation = False
      self.ui.pushAddElucidation.hide()
      return

    self.ui.pushAddElucidation.show()

  def on_pushAddElucidation_pressed(self):  # TODO: fix
    self.load_elucidation = True
    self.ui.pushAddElucidation.hide()
    text_ID = self.selected_item.text(0)
    predicate = self.selected_item.predicate
    if self.__hasElucidation(text_ID, predicate):
      p = self.__makePathName(text_ID)
      d = self.ui.textElucidation.toPlainText()
      self.elucidations[p] = d
      pass

  def on_treeClass_itemPressed(self, item, column):

    text_ID = item.text(column)

    self.debugging("you picked column %s with id %s" % (column, text_ID),
                   self.dataModel.whatIsThis(self.current_class, text_ID))

    try:
      predicate = item.predicate
    except:
      item.predicate = None
      predicate = None
    self.selected_item = item
    self.debugging("column ", column)

    item.setSelected(True)
    # self.selected_item.setBackground(item.columnCount(),QBRUSHES["selected"])

    if self.previously_selected_item:
      self.debugging("column ", self.previously_selected_item.columnCount())
      # self.previously_selected_item.setBackground(column, QBRUSHES["unselect"])
      self.previously_selected_item = self.selected_item

    # if text_ID in self.class_names:
    if self.dataModel.isClass(text_ID):
      self.debugging("-- is class", text_ID)
      self.__ui_state("selected_class")
      self.current_class_or_subclass = text_ID
      if self.current_class != text_ID:
        self.__shiftClass(text_ID)
      if self.dataModel.isRoot(text_ID):
        self.debugging("-- is root", text_ID)
        self.__ui_state("selected_root")
    elif self.dataModel.isLinkedWidth(self.current_class, text_ID):
      self.debugging("-- is linked", text_ID)
      self.__ui_state("is_linked")
      self.current_class_or_subclass = text_ID
    elif self.dataModel.isSubClass(self.current_class, text_ID):
      self.debugging("-- it is a subclass", text_ID)
      self.__ui_state("selected_subclass")
      self.current_class_or_subclass = text_ID
      if not self.__permittedClasses():
        self.debugging(">> no_existing_classes")
        self.__ui_state("no_existing_classes")
      else:
        self.debugging("--selected_subclass")
        self.__ui_state("selected_subclass")
      self.current_class_or_subclass = text_ID
    elif self.dataModel.isPrimitive(self.current_class, predicate):
      self.debugging("-- is a primitive", predicate)
      self.__ui_state("selected_primitive")
    elif self.dataModel.isValue(predicate):
      self.__ui_state("value_selected")
      self.debugging("-- isvalue", predicate)
    else:
      print("should not come here")

    if self.dataModel.getElucidationList(self.current_class):
      self.ui.pushAddElucidation.hide()
      self.load_elucidation = True
      p = self.__makePathName(text_ID)
      not_exist = None
      try:
        self.ui.textElucidation.setPlainText(self.elucidations[p])
      except:
        not_exist = p
        self.ui.textElucidation.clear()

      if not_exist:
        self.elucidations[not_exist] = ""

    self.ui.treeClass.clearSelection()

  def on_treeClass_itemDoubleClicked(self, item, column):
    # print("debugging -- double click", item.text(0))
    ID = str(item.text(column))
    predicate = item.predicate
    if self.dataModel.isSubClass(self.current_class, ID):
      predicate = "is_a_subclass_of"
      # rename subclass

      prompt = "new name"
      placeholder = str(item.text(0))

      new_name = self.__getConstraintString(placeholder, prompt)
      if new_name:
        self.__renameItemInGraph(ID, new_name, predicate)
      # print("debugging -- renaming")F

  def on_pushAddSubclass_pressed(self):
    # print("debugging -- add subclass")

    # get an identifier for the subclass
    prompt = "name for subclass"
    subClass = self.__getConstraintString(prompt)

    if not subClass:
      return

    # elucidation
    p = self.__makePathName(subClass)
    self.elucidations[p] = None
    self.ui.textElucidation.clear()

    # add to graph
    self.dataModel.addSubclass(self.current_class, self.current_class_or_subclass, subClass)

    # generate GUI tree
    self.__createTree(self.current_class)
    self.changed = True

  def on_pushAddPrimitive_pressed(self):
    self.debugging("add primitive first")
    # forbidden = self.subclass_names[self.current_class]

    prompt = "name for primitive"
    primitive_ID = self.__getConstraintString(prompt)
    self.debugging("debugging -- ", primitive_ID)
    if not primitive_ID:
      return

    permitted_classes = PRIMITIVES
    dialog2 = UI_stringSelector("hello", permitted_classes)
    dialog2.exec()

    # print("debugging")
    primitive_class = dialog2.getSelection()
    if not primitive_class:
      return
    self.debugging("add primitive")
    # self.value_names[self.current_class].append(primitive_ID)

    # add to graph
    item = self.__addItemToTree(primitive_ID, "value", self.current_class_or_subclass)
    self.__addItemToTree(primitive_class, primitive_class, primitive_ID, parent_item=item)
    # if self.current_subclass not in self.primitives[self.current_class]:
    #   self.primitives[self.current_class][self.current_subclass] = []
    # self.primitives[self.current_class][self.current_subclass].append(primitive_ID)
    self.debugging("end of add")

  def on_pushAddNewClass_pressed(self):
    # print("debugging -- add class")

    prompt = "name for subclass"
    Class = self.__getConstraintString(prompt)
    if not Class:
      return

    self.dataModel.addClass(Class)

    # elucidation
    self.ui.textElucidation.clear()
    self.elucidations[Class] = None

    # make link
    self.dataModel.addLink(self.current_class, Class, self.current_class_or_subclass)

    self.__createTree(Class)
    self.__addToClassPath(addclass=Class)
    self.current_class = Class
    self.changed = True
    self.__ui_state("show_tree")

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
      subject = makeRDFCompatible(Class)
      object = makeRDFCompatible(self.current_class_or_subclass)
      self.dataModel.GRAPHS[self.current_class].add((subject, RDFSTerms["link_to_class"], object))

      parent_item = self.ui.treeClass.currentItem()
      item = QTreeWidgetItem(parent_item)
      item.setText(0, Class)
      p = "link_to_class"
      item.predicate = p
      # item.setBackground(0, LINK_COLOUR)
      item.setForeground(0, QBRUSHES[p])
      self.ui.treeClass.expandAll()
      self.changed = True

  def on_pushRemoveClass_pressed(self):

    item = self.selected_item
    Class = item.text(0)
    self.debugging("found class to be removed")
    self.dataModel.removeClass(Class)
    self.__removeClassPath(Class)

    self.current_class = self.class_path[-1]
    origin = self.current_class
    self.__createTree(origin)
    self.__ui_state("show_tree")

  def on_pushRemoveClassLink_pressed(self):

    removed_class = self.dataModel.removeLinkInClass(self.current_class, self.current_class_or_subclass)
    self.__checkForUnusedClasses(removed_class)
    self.__createTree(self.current_class)
    self.__ui_state("show_tree")

  def on_pushSave_pressed(self):
    # print("debugging -- pushSave")

    conjunctiveGraph = self.__prepareConjunctiveGraph()
    self.__writeQuadFile(conjunctiveGraph, self.project_file_name)
    self.changed = False

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

    fname = file_name + ".%s" % FILE_FORMAT
    self.project_file_name = os.path.join(ONTOLOGY_REPOSITORY, fname)
    self.__writeQuadFile(conjunctiveGraph, self.project_file_name)

    dot = self.__makeDotGraph()

    self.changed = False

  def on_pushLoad_pressed(self):
    dialog = QFileDialog.getOpenFileName(None,
                                         "Load Ontology",
                                         ONTOLOGY_REPOSITORY,
                                         "*.%s" % FILE_FORMAT,
                                         )
    self.project_file_name = dialog[0]
    if dialog[0] == "":
      return

    self.dataModel = DataModel()

    self.dataModel.loadFromFile(self.project_file_name)
    self.current_class = ROOTCLASS
    self.__addToClassPath(ROOTCLASS)
    self.__createTree(self.current_class)
    self.__ui_state("show_tree")

  def on_listClasses_itemClicked(self, item):
    Class = item.text()
    self.__shiftClass(Class)

  def on_pushVisualise_pressed(self):

    dot = self.__makeDotGraph()
    dot.view()

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
    # self.current_subclass = origin
    self.__ui_state("show_tree")

  def __prepareTree(self, origin):
    graph = self.dataModel.GRAPHS[self.current_class]  # CLASSES[self.current_class]
    print(graph.serialize(format='turtle'))
    # print("debugging", origin)
    tuples_plus = []
    for subject, predicate, object_ in graph.triples((None, None, None)):
      try:
        s = extractNameFromClassURI(subject)
        p = MYTerms[predicate]
        o = extractNameFromClassURI(object_)
        if p not in PRIMITIVES:
          tuples_plus.append((s, o, p))
        else:
          tuples_plus.append((o, s, p))
      except:
        pass
    return tuples_plus

  def __prepareConjunctiveGraph(self):
    conjunctiveGraph = ConjunctiveGraph("Memory")
    namespaces = self.dataModel.namespaces
    for ns in namespaces:
      conjunctiveGraph.bind(ns, namespaces[ns])
    for cl in self.dataModel.getClassNamesList():  # class_definition_sequence:
      uri = self.dataModel.makeURI(cl, cl)  # TODO: check
      for s, p, o in self.dataModel.GRAPHS[cl].triples((None, None, None)):
        # print(s, p, o)
        conjunctiveGraph.get_context(namespaces[cl]).add((s, p, o))
    return conjunctiveGraph

  def __prepareJsonData(self):
    data = {}
    graphs = {}
    for cl in self.dataModel.getClassNamesList():
      graphs[cl] = []
      for s, p, o in self.dataModel.GRAPHS[cl].triples((None, None, None)):
        my_p = MYTerms[p]
        graphs[cl].append((s, my_p, o))
    data["root"] = ROOTCLASS
    data["graphs"] = graphs
    data["elucidations"] = self.elucidations
    return data

  def __removeClass(self, Class):
    self.dataModel.removeClass(Class)
    self.__cutClassPath(Class)

    # self._
    # self.__removeClassPath(Class)
    # # previous_class = self.class_definition_sequence.index(Class)
    # # self.current_class = self.class_definition_sequence[previous_class - 1]
    # # self.class_definition_sequence.remove(Class)
    # self.__cutClassPath(Class)
    # self.debugging(("--cleaned class list"))
    # self.debugging("--cleand class sequence", self.class_path)
    # del self.dataModel.GRAPHS[Class]
    # # remove links
    # rdfClass = makeRDFCompatible(Class)
    # for Class in self.dataModel.GRAPHS:
    #   for t in self.dataModel.GRAPHS[Class].triples((rdfClass, None, None)):
    #     self.dataModel.GRAPHS[Class].remove(t)
    # self.__createTree(self.current_class)
    # pass
    #
    # # clean out elucidations associated with the deleted class
    # elucidations = copy.copy(self.elucidations)
    # for e in elucidations:
    #   if Class in e:
    #     del self.elucidations[e]

    self.changed = True

  def __checkForUnusedClasses(self, removed_classs):
    current_set_of_classes = set(self.dataModel.GRAPHS.keys())
    used_classes_set = set([])
    for c in current_set_of_classes:
      if c not in removed_classs:
        for s, p, o in self.dataModel.GRAPHS[c].triples((None, None, None)):
          if (str(s) in current_set_of_classes) or (extractNameFromClassURI(o) in current_set_of_classes):
            used_classes_set.add(c)
    # not used classes:
    not_used_classes = current_set_of_classes - used_classes_set
    self.debugging("not used set of classes: ", not_used_classes)

    to_remove_classes = set()

    not_used_classes = not_used_classes
    for c in not_used_classes:
      untreated_classes = not_used_classes - to_remove_classes
      dialog = UI_stringSelector("you got unused classes -- select the one you want to delete or cancel",
                                 untreated_classes)
      dialog.exec()
      selection = dialog.getSelection()
      if selection:
        self.__removeClass(selection)
        untreated_classes.remove(selection)
      else:
        break

  def __writeQuadFile(self, conjunctiveGraph, f):
    saveBackupFile(f)
    inf = open(f, 'w')
    inf.write(conjunctiveGraph.serialize(format=FILE_FORMAT))
    inf.close()
    print("written to file ", f)

  def __makeTree(self, touples, origin=[], stack=[], items={}):
    for s, o, p in touples:
      if (s, o, p) not in stack:
        if s != origin:
          if o in items:
            # print("add %s <-- %s" % (o, s),p)
            item = QTreeWidgetItem(items[o])
            # print("debugging -- color",p )
            # item.setBackground(0, COLOURS[p])
            item.predicate = p
            item.setForeground(0, QBRUSHES[p])
            stack.append((s, o, p))
            item.setText(0, s)
            items[s] = item
            self.__makeTree(touples, origin=s, stack=stack, items=items)

  def __renameItemInGraph(self, ID, new_name, predicate):
    graph = self.dataModel.GRAPHS[self.current_class]
    for s, p, o in graph.triples((None, None, Literal(ID))):
      # print("debugging -- change triple", s, p, o)
      self.dataModel.GRAPHS[self.current_class].remove((s, p, o))
      object = makeRDFCompatible(new_name)
      self.dataModel.GRAPHS[self.current_class].add((s, RDFSTerms[predicate], object))
    for s, p, o in graph.triples((Literal(ID), None, None)):
      # print("debugging -- change triple", s, p, o)  # add to graph
      self.dataModel.GRAPHS[self.current_class].remove((s, p, o))
      subject = makeRDFCompatible(new_name)
      self.dataModel.GRAPHS[self.current_class].add((subject, RDFSTerms[predicate], o))
    self.__createTree(self.current_class)
    self.__ui_state("show_tree")

  def __makePathName(self, text_ID):
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
    object = self.dataModel.makeURI(self.current_class, internal_object)
    subject = self.dataModel.makeURI(self.current_class, internal_subject)
    self.dataModel.GRAPHS[self.current_class].add((subject, RDFSTerms[predicate], object))
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
    permitted_classes = []
    for cl in self.dataModel.GRAPHS:
      if cl != self.current_class:
        if cl not in self.dataModel.getLinkList(cl):  # link_lists[cl]:
          if cl not in self.class_path:
            permitted_classes.append(cl)
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
    graph_overall = Graph()
    for cl in self.dataModel.GRAPHS:
      for t in self.dataModel.GRAPHS[cl].triples((None, None, None)):
        graph_overall.add(t)
    dot = plot(graph_overall, self.dataModel.getAllNames())  # class_names)
    # print("debugging -- dot")
    graph_name = ROOTCLASS
    file_name = graph_name + ".pdf"
    file_path = os.path.join(ONTOLOGY_REPOSITORY, file_name)
    if os.path.exists(file_path):
      saveBackupFile(file_path)
    dot.render(graph_name, directory=ONTOLOGY_REPOSITORY)
    return dot

  # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s
  def mousePressEvent(self, event, QMouseEvent=None):
    self.dragPos = event.globalPosition().toPoint()

  def mouseMoveEvent(self, event, QMouseEvent=None):
    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
    self.dragPos = event.globalPosition().toPoint()


if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = OntobuilderUI()
  MainWindow.show()
  sys.exit(app.exec())
