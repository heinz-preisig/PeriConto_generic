import os
import sys

from PeriContoBackEnd import BackEnd
from PeriContoSemantics import FILE_FORMAT

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *

# from graphHAP import Graph
from PeriContoSchemaBricks_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.ui_combo_dialog_impl import UI_ComboDialog
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String

# from PeriConto import debugging
from PeriContoSemantics import ONTOLOGY_REPOSITORY

DEBUGG = True


def debugging(*info):
  if DEBUGG:
    print("debugging", info)


COLOURS = {
        "ROOT"         : QtGui.QColor(0, 199, 255),
        "is_member"    : QtGui.QColor(0, 0, 0, 255),
        "is_defined_by": QtGui.QColor(255, 100, 5, 255),
        "value"        : QtGui.QColor(230, 165, 75),
        "data_type"    : QtGui.QColor(100, 100, 100),
        "integer"      : QtGui.QColor(155, 155, 255),
        "decimal"      : QtGui.QColor(155, 155, 255),
        "string"       : QtGui.QColor(255, 200, 200, 255),
        "comment"      : QtGui.QColor(155, 155, 255),
        "uri"          : QtGui.QColor(255, 200, 200, 255),
        "boolean"      : QtGui.QColor(255, 200, 200, 255),
        "selected"     : QtGui.QColor(252, 248, 192, 255),
        "unselect"     : QtGui.QColor(255, 255, 255, 255),
        }

QBRUSHES = {}
for c_hash in COLOURS.keys():
  QBRUSHES[c_hash] = QtGui.QBrush(COLOURS[c_hash])

LINK_COLOUR = QtGui.QColor(255, 100, 5, 255)
PRIMITIVE_COLOUR = QtGui.QColor(255, 3, 23, 255)


class GUIMessage(dict):
  def __init__(self, event=None, name=None, type=None, parent=None):
    super().__init__()
    self["event"] = event
    self["name"] = name
    self["type"] = type
    self["parent"] = parent


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
            "brick_control"         : self.ui.groupBoxBricksControl,
            "brick_create"          : self.ui.pushBrickCreate,
            "brick_delete"          : self.ui.pushBrickRemove,
            "brick_rename"          : self.ui.pushBrickRename,
            "brick_add_item"        : self.ui.pushBrickAddItem,
            "brick_remove_item"     : self.ui.pushBrickRemoveItem,
            "brick_add_primitive"   : self.ui.pushBrickAddPrimitive,
            "brick_rename_item":     self.ui.pushBrickItemOrPrimitiveRename,
            "brick_list"            : self.ui.listBricks,
            "brick_tree"            : self.ui.brickTree,
            "tree_control"          : self.ui.groupBoxTreesControl,
            "tree_create"           : self.ui.pushTreeCreate,
            "tree_delete"           : self.ui.pushDeleteTree,
            "tree_add_link"         : self.ui.pushTreeLinkExistingClass,
            "tree_remove_link"      : self.ui.pushTreeRemoveClassLink,
            "tree_instantiate"      : self.ui.pushTreeInstantiate,
            "tree_visualise"        : self.ui.pushTreeVisualise,
            "tree_select_brick"     : self.ui.comboBoxTreeSelectBrick,
            "Tree"                  : self.ui.treeTree,
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
    self.changed = False

  def setInterface(self, shows, hides):
    pass
    for show in shows:
      self.gui_objects[show].show()
    for hide in hides:
      self.gui_objects[hide].hide()

  def on_pushOntologyCreate_pressed(self):
    debugging("-- pushOntologyCreate")

    dialog = UI_String("provide new ontology name", placeholdertext="ontology name")
    dialog.exec()
    name = dialog.text
    if name:
      event = "create ontology"
    else:
      event = "start"

    message = GUIMessage(event=event, name=name.upper())
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
    project_name = os.path.basename(file_spec).split(os.path.extsep)[0].split("+")[0]
    message = GUIMessage(event="load ontology", name=project_name)
    self.backend.processEvent(message)

  def on_pushOntologySave_pressed(self):
    debugging("-- pushOntologySave")
    event = "save"
    message = GUIMessage(event=event)
    self.backend.processEvent(message)

  def on_pushOntologySaveAs_pressed(self):
    debugging("-- pushOntologySaveAs")
    event = "save as"
    message = GUIMessage(event=event)

  def on_pushBrickCreate_pressed(self):
    debugging("-- pushBrickCreate")
    dialog = UI_String("new brick", "brick name", self.brickList)
    dialog.exec()
    name = dialog.text
    if name:
      event = "new brick"
    else:
      event = None
    message = GUIMessage(event=event, name=name.upper())
    self.backend.processEvent(message)

  def on_pushBrickRemove_pressed(self):
    message = GUIMessage()
    debugging("--pushBrickRemove")

  def on_pushBrickAddItem_pressed(self):
    debugging("-- pushBrickAddItem")
    event = "asks for adding an item"
    message = GUIMessage(event=event)
    self.backend.processEvent(message)

  def askForItemName(self, prompt, existing_names):
    dialog = UI_String(prompt,
                       placeholdertext="item name",
                       limiting_list=existing_names)
    dialog.exec()
    name = dialog.text
    return name

  def askForPrimitiveType(self, primitives):
    # self.ui.comboBoxPrimitives.show()
    dialog = UI_ComboDialog("select primitive", primitives)
    primitive = dialog.getSelection()
    return primitive

  def setPrimitives(self, PRIMITIVES):
    self.ui.comboBoxPrimitives.clear()
    self.ui.comboBoxPrimitives.addItems(PRIMITIVES)

  def on_pushBrickRemoveItem_pressed(self):
    message = GUIMessage(event="remove item from brick tree")
    debugging("-- pushBrickRemoveItem")
    self.backend.processEvent(message)

  def on_pushBrickAddPrimitive_pressed(self):
    item = self.ui.brickTree.currentItem()
    name = item.text(0)
    parent_name = item.parent_name
    debugging("-- pushBrickAddPrimitive")
    event = "ask for adding a primitive"
    message = GUIMessage(event=event,
                         name=name,
                         type=item.predicate,
                         parent=parent_name)
    self.backend.processEvent(message)

  def on_pushBrickRename_pressed(self):
    event = "rename brick"
    message = GUIMessage(event= event)
    self.backend.processEvent(message)
    debugging("-- pushBrickRename")

  def on_pushBrickItemOrPrimitiveRename_pressed(self):
    event = "rename item/primitive"
    message = GUIMessage(event=event)
    self.backend.processEvent(message)

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
    event = "selected brick"
    message = GUIMessage(event=event, name=name)
    self.backend.processEvent(message)

  def on_listTrees_itemClicked(self, item):
    name = item.text()
    debugging("-- listTrees -- item", name)
    event = "selectedTree"

  def on_brickTree_itemClicked(self, item, column):
    name = item.text(column)
    debugging("-- brick tree item %s, column %s" % (name, column))
    parent_name = item.parent_name
    event = "item in brick tree selected"
    message = GUIMessage(event=event,
                         name=name,
                         type=item.predicate,
                         parent=parent_name)
    self.backend.processEvent(message)

  def on_treeTree_itemClicked(self, item, column):
    name = item.text()
    debugging("-- tree item %s, column %s" % (name, column))

  def showBrickList(self, brickList):
    self.brickList = brickList
    self.ui.listBricks.clear()
    self.ui.listBricks.addItems(brickList)

  def showBrickTree(self, tuples, origin):

    # def __createTree(self, origin):
    widget = self.ui.brickTree
    self.__instantiateTree(origin, tuples, widget)

  def showTreeTree(self, tuples, origin):
    widget = self.ui.treeTree
    self.__instantiateTree(origin, tuples, widget)


  def __instantiateTree(self, origin, tuples, widget):
    widget.clear()
    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = origin
    rootItem.setText(0, origin)
    rootItem.setSelected(False)
    rootItem.parent_name = None
    rootItem.predicate = None
    widget.addTopLevelItem(rootItem)
    self.current_class = origin
    self.__makeTree(tuples, origin=origin, stack=[], items={origin: rootItem})
    widget.show()
    widget.expandAll()

  def __makeTree(self, tuples, origin=[], stack=[], items={}):
    for q in tuples:
      if q not in stack:
        s, p, o, dir = q
        # print("processing",s,p,o)
        if s != origin:
          if o in items:
            # if s != "":
            item = QTreeWidgetItem(items[o])
            item.parent_name = o
            item.predicate = p
            item.setForeground(0, QBRUSHES[p])
            stack.append(q)  # (s, p, o))
            if s == "":
              item.setText(0,p)
            else:
              item.setText(0, s)
            items[s] = item
            print("items", s,p,o)
            self.__makeTree(tuples, origin=s, stack=stack, items=items)

  # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s
  def mousePressEvent(self, event, QMouseEvent=None):
    self.dragPos = event.globalPosition().toPoint()

  def mouseMoveEvent(self, event, QMouseEvent=None):
    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
    self.dragPos = event.globalPosition().toPoint()

  def markChanged(self):
    self.changed = True

  def on_pushExit_pressed(self):
    self.closeMe()

  def markSaved(self):
    self.changed = False

  def closeMe(self):
    if self.changed:
      dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
      if dialog == "YES":
        self.on_pushOntologySave_pressed()
      elif dialog == "NO":
        pass
    else:
      pass
    sys.exit()

  # def __ui_state(self, state):
  #   # what to show
  #   if state == "start":
  #     show = ["load",
  #             "create",
  #             "exit",
  #             ]
  #   elif state == "show_tree":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "visualise",
  #             ]
  #   elif state == "selected_subclass":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "add_subclass",
  #             "add_primitive",
  #             "link_new_class",
  #             "link_existing_class",
  #             "remove_subclass",
  #             "elucidation",
  #             ]
  #   elif state == "selected_root":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "add_subclass",
  #             "add_primitive",
  #             "elucidation",
  #             ]
  #   elif state == "selected_class":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "add_subclass",
  #             "add_primitive",
  #             "elucidation",
  #             "remove_class",
  #             ]
  #   elif state == "selected_primitive":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             ]
  #   elif state == "selected_value":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "elucidation",
  #             "remove_primitive"
  #             ]
  #   elif state == "no_existing_classes":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "add_subclass",
  #             "add_primitive",
  #             "link_new_class",
  #             "elucidation",
  #             ]
  #   elif state == "is_linked":
  #     show = ["save",
  #             "save_as",
  #             "exit",
  #             "add_primitive",
  #             "elucidation",
  #             "remove_class_link",
  #             ]
  #   else:
  #     show = []
  #
  #   for b in self.gui_objects:
  #     if b not in show:
  #       self.gui_objects[b].hide()
  #     else:
  #       self.gui_objects[b].show()

  # def debugging(self, *info):
  #   if self.DEBUGG:
  #     print("debugging", info)

  # def on_pushCreate_pressed(self):
  #   dialog = UI_String("name for your ontology file",
  #                      placeholdertext="file name extension is default")
  #   dialog.exec()
  #   name = dialog.getText()
  #   self.project_name = name
  #   if name:
  #     self.project_file_spec = os.path.join(ONTOLOGY_REPOSITORY, name + ".%s" % FILE_FORMAT)
  #   else:
  #     return
  #
  #   self.dataModel = DataModel()
  #   self.current_class = ROOTCLASS
  #   self.class_path = [ROOTCLASS]
  #   self.ui.listClasses.addItems(self.class_path)  # make class list
  #   self.changed = True
  #
  #   self.__createTree(ROOTCLASS)

  # def on_textElucidation_textChanged(self):
  #   print("debugging change text", self.ui.textElucidation.toPlainText())
  #   # self.current_class
  #   # self.current_item_ID
  #
  #   self.ui.pushAddElucidation.show()
  #
  # def on_pushAddElucidation_pressed(self):  # TODO: fix
  #   elucidation = self.ui.textElucidation.toPlainText()
  #   print("not implemented")
  #   # print("debugging elucidations", elucidation)
  #   # self.dataModel.addElucidation(elucidation, self.current_class, self.current_item_ID)
  #   pass
  #
  #   # self.load_elucidation = True
  #   # self.ui.pushAddElucidation.hide()
  #   # text_ID = self.selected_item.text(0)
  #   # predicate = self.selected_item.predicate
  #   # if self.__hasElucidation(text_ID, predicate):
  #   #   p = self.__makePathName(text_ID)
  #   #   d = self.ui.textElucidation.toPlainText()
  #   #   self.elucidations[p] = d
  #   #   pass
  #
  # def on_treeClass_itemPressed(self, item, column):
  #
  #   button = QApplication.instance().mouseButtons().name
  #   text_ID = item.text(column)
  #   if button == "RightButton":
  #     # print("right button pressed")
  #     if ELUCIDATION in text_ID:
  #       makeMessageBox("cannot be renamed ", buttons=["OK"])
  #       return
  #     ID = str(text_ID)
  #     is_subclass = self.dataModel.isSubClass(self.current_class, ID)
  #     is_value = self.dataModel.isValue(self.current_class, ID)
  #     if (is_subclass or is_value):
  #       prompt = "new name"
  #       placeholder = str(item.text(0))
  #
  #       new_name = self.__getConstraintString(placeholder, prompt)
  #       if new_name:
  #         self.__renameItemInGraph(ID, new_name)
  #     return
  #   elif button == "MiddleButton":
  #     print("middle button pressed -- no action")
  #     return
  #
  #   else:  # button == "LeftButton":
  #     # print("left button pressed")
  #     pass
  #
  #   self.current_item_ID = text_ID
  #
  #   debugging("you picked column %s with id %s" % (column, text_ID),
  #             self.dataModel.what_is_this(self.current_class, text_ID))
  #
  #   try:
  #     predicate = item.predicate
  #   except:
  #     print(">>>>>>>>>>>>>>>>> no predicate")
  #     item.predicate = None
  #     predicate = None
  #   self.selected_item = item
  #   debugging("column ", column)
  #
  #   item.setSelected(True)  # sets background
  #
  #   if self.previously_selected_item:  # TODO: needed?
  #     debugging("column ", self.previously_selected_item.columnCount())
  #     # self.previously_selected_item.setBackground(column, QBRUSHES["unselect"])
  #     self.previously_selected_item = self.selected_item
  #
  #   # if text_ID in self.class_names:
  #   is_root = self.dataModel.isRoot(text_ID)
  #   isclass = self.dataModel.isClass(text_ID)
  #   is_linked_with = self.dataModel.isLinkedWidth(self.current_class, text_ID)
  #   is_item = self.dataModel.isSubClass(self.current_class, text_ID)
  #   is_primitive = self.dataModel.isPrimitive(self.current_class, text_ID)
  #   is_value = self.dataModel.isValue(self.current_class, text_ID)
  #   is_elucidation = self.dataModel.isElucidation(self.current_class, text_ID)
  #   is_comment = text_ID == "comment"
  #
  #   if isclass:  # set gui state
  #     debugging("-- is class", text_ID)
  #     self.__ui_state("selected_class")
  #     if self.current_class != text_ID:
  #       self.__shiftClass(text_ID)
  #     if is_root:
  #       debugging("-- is root", text_ID)
  #       self.__ui_state("selected_root")
  #   elif is_linked_with:
  #     debugging("-- is linked", text_ID)
  #     self.__ui_state("is_linked")
  #   elif is_item:
  #     debugging("-- it is a subclass", text_ID)
  #     self.__ui_state("selected_subclass")
  #   elif is_primitive:
  #     debugging("-- is a primitive", predicate)
  #     self.__ui_state("selected_primitive")
  #   elif is_value:
  #     self.__ui_state("selected_value")
  #     debugging("-- isvalue", predicate)
  #   elif is_elucidation:
  #     pass
  #   else:
  #     print("should not come here")
  #     self.__ui_state("show_tree")
  #
  #   # if self.dataModel.getElucidationList(self.current_class):
  #   #   self.ui.pushAddElucidation.hide()
  #   #   self.load_elucidation = True
  #   #   p = self.__makePathName(text_ID)
  #   #   not_exist = None
  #   #   try:
  #   #     self.ui.textElucidation.setPlainText(self.elucidations[p])
  #   #   except:
  #   #     not_exist = p
  #   #     self.ui.textElucidation.clear()
  #   #
  #   #   if not_exist:
  #   #     self.elucidations[not_exist] = ""
  #
  #   self.ui.treeClass.clearSelection()
  #
  # def on_pushAddSubclass_pressed(self):
  #   # print("debugging -- add subclass")
  #
  #   # get an identifier for the subclass
  #   prompt = "name for subclass"
  #   subClass = self.__getConstraintString(prompt)
  #
  #   if not subClass:
  #     return
  #
  #   # elucidation
  #   p = self.__makePathName(subClass)  # TODO add elucidation handling
  #   # self.elucidations[p] = None
  #   # self.ui.textElucidation.clear()
  #
  #   # add to graph
  #   self.dataModel.addSubclass(self.current_class, self.current_item_ID, subClass)
  #
  #   # generate GUI tree
  #   self.__createTree(self.current_class)
  #   self.changed = True
  #
  # def on_pushRemoveSubClass_pressed(self):
  #   pass
  #   itemID = self.current_item_ID
  #   Class = self.current_class
  #   self.dataModel.removeSubClass(Class, itemID)
  #   self.__createTree(self.current_class)
  #   self.changed = True
  #
  # def on_pushAddPrimitive_pressed(self):
  #   debugging("add primitive first")
  #   # forbidden = self.subclass_names[self.current_class]
  #
  #   prompt = "name for primitive"
  #   primitive_ID = self.__getConstraintString(prompt)
  #   debugging("debugging -- ", primitive_ID)
  #   if not primitive_ID:
  #     return
  #
  #   permitted_classes = PRIMITIVES
  #   dialog2 = UI_stringSelector("choose primitive", permitted_classes)
  #   dialog2.exec()
  #
  #   primitive_class = dialog2.getSelection()
  #   if not primitive_class:
  #     return
  #   debugging("add primitive")
  #   self.dataModel.addPrimitive(self.current_class, self.current_item_ID, primitive_ID, primitive_class)
  #   debugging("end of add")
  #   self.__createTree(self.current_class)
  #   self.changed = True
  #
  # def on_pushAddNewClass_pressed(self):
  #   # print("debugging -- add class")
  #
  #   prompt = "name for subclass"
  #   Class = self.__getConstraintString(prompt)
  #   if not Class:
  #     return
  #
  #   newClass = Class.upper()
  #
  #   self.dataModel.addClass(newClass)
  #
  #   # elucidation
  #   self.ui.textElucidation.clear()
  #   self.elucidations[Class] = None
  #
  #   # make link
  #   self.dataModel.addLink(self.current_class, newClass, self.current_item_ID)
  #
  #   self.__createTree(newClass)
  #   self.__addToClassPath(addclass=newClass)
  #   self.current_class = newClass
  #   self.__ui_state("show_tree")
  #   self.changed = True
  #
  # def on_pushAddExistingClass_pressed(self):
  #   permitted_classes = self.__permittedClasses()
  #
  #   # permitted_classes
  #   if permitted_classes:
  #     dialog = UI_stringSelector("select", permitted_classes)
  #     dialog.exec()
  #     selection = dialog.getSelection()
  #     if not selection:
  #       return
  #
  #     Class = selection
  #     _, object = self.dataModel.makeClassURI(Class)
  #     subject = self.dataModel.makeURI(self.current_class, self.current_item_ID)
  #     triple = (subject, RDFSTerms["is_defined_by"], object)
  #     self.dataModel.GRAPHS[self.current_class].add(triple)
  #     print("adding triple:", triple)
  #
  #     parent_item = self.ui.treeClass.currentItem()
  #     item = QTreeWidgetItem(parent_item)
  #     item.setText(0, Class)
  #     p = "is_defined_by"
  #     item.predicate = p
  #     # item.setBackground(0, LINK_COLOUR)
  #     item.setForeground(0, QBRUSHES[p])
  #     self.ui.treeClass.expandAll()
  #     self.changed = True
  #
  # def on_pushRemoveClass_pressed(self):
  #
  #   item = self.selected_item
  #   Class = item.text(0)
  #   self.dataModel.removeClass(Class)
  #
  #   self.class_path.remove(Class)
  #   previous_class = self.class_path[-1]
  #   self.current_class = previous_class
  #   self.__shiftClass(previous_class)
  #   self.changed = True
  #
  # def on_pushRemoveClassLink_pressed(self):
  #
  #   removed_class = self.dataModel.removeLinkInClass(self.current_class, self.current_item_ID)
  #   # self.__checkForUnusedClasses(removed_class)
  #   self.dataModel.checkForClassIsUsed((removed_class))
  #   self.__createTree(self.current_class)
  #   self.__ui_state("show_tree")
  #   self.changed = True
  #
  # def on_pushSave_pressed(self):
  #   # print("debugging -- pushSave")
  #
  #   conjunctiveGraph = self.__prepareConjunctiveGraph()
  #   self.__writeQuadFile(conjunctiveGraph, self.project_file_spec)
  #
  #   project_file_spec_json = os.path.join(ONTOLOGY_REPOSITORY, self.project_name + ".%s" % FILE_FORMAT_)
  #
  #   self.__writeQuadFile(conjunctiveGraph, project_file_spec_json)
  #
  #   self.changed = False
  #
  # def on_pushRemovePrimitive_pressed(self):
  #   self.dataModel.removePrimitive(self.current_class, self.current_item_ID)
  #
  #   self.__createTree(self.current_class)
  #   self.__ui_state("show_tree")
  #
  #   self.change = True
  #
  # def on_pushSaveAs_pressed(self):
  #
  #   conjunctiveGraph = self.__prepareConjunctiveGraph()
  #
  #   dialog = QFileDialog.getOpenFileName(None,
  #                                        "save Ontology as",
  #                                        ONTOLOGY_REPOSITORY,
  #                                        "*.%s" % FILE_FORMAT,
  #                                        )
  #   file_name = dialog[0]
  #   if not file_name:
  #     file_names = []
  #     for file in glob.glob("%s/*.%s" % (ONTOLOGY_REPOSITORY, FILE_FORMAT)):
  #       basename = os.path.basename(file)
  #       name, _ = basename.split(".")
  #       file_names.append(name)
  #
  #     dialog = UI_String("name for subclass", limiting_list=file_names)
  #     dialog.exec()
  #     file_name = dialog.getText()
  #     if not file_name:
  #       return
  #   else:
  #     file_name = file_name.split(".")[0]
  #
  #   for f_format in [FILE_FORMAT, FILE_FORMAT_]:
  #     fname = file_name + ".%s" % f_format
  #     self.project_file_spec = os.path.join(ONTOLOGY_REPOSITORY, fname)
  #     self.__writeQuadFile(conjunctiveGraph, self.project_file_spec)
  #
  #   dot = self.__makeDotGraph()
  #
  #   self.changed = False
  #
  # def on_pushLoad_pressed(self):
  #   dialog = QFileDialog.getOpenFileName(None,
  #                                        "Load Ontology",
  #                                        ONTOLOGY_REPOSITORY,
  #                                        "*.%s" % FILE_FORMAT,
  #                                        )
  #   self.project_file_spec = dialog[0]
  #   self.project_name = os.path.basename(self.project_file_spec).split(os.path.extsep)[0]
  #   if dialog[0] == "":
  #     return
  #
  #   self.dataModel = DataModel()
  #
  #   self.dataModel.loadFromFile(self.project_file_spec)
  #   self.current_class = ROOTCLASS
  #   self.__addToClassPath(ROOTCLASS)
  #   self.__createTree(self.current_class)
  #   self.__ui_state("show_tree")
  #
  # def on_listClasses_itemClicked(self, item):
  #   Class = item.text()
  #   self.__shiftClass(Class)
  #
  # def on_pushVisualise_pressed(self):
  #
  #   dot = self.__makeDotGraph()
  #
  #
  # def __createTree(self, origin):
  #   widget = self.ui.treeClass
  #   widget.clear()
  #
  #   rootItem = QTreeWidgetItem(widget)
  #   widget.setColumnCount(1)
  #   rootItem.root = origin
  #   rootItem.setText(0, origin)
  #   rootItem.setSelected(False)
  #   rootItem.predicate = None
  #   widget.addTopLevelItem(rootItem)
  #   self.current_class = origin
  #   tuples = self.__prepareTree(origin)
  #   self.__makeTree(tuples, origin=origin, stack=[], items={origin: rootItem})
  #   widget.show()
  #   widget.expandAll()
  #   self.__ui_state("show_tree")
  #
  # def __prepareTree(self, origin):
  #   graph = self.dataModel.GRAPHS[origin]  # self.current_class]
  #   debugging(graph.serialize(format="turtle"))
  #   # print("debugging", origin)
  #   tuples_plus = []
  #   for subject, predicate, object in graph.triples((None, None, None)):
  #     debugging("--", subject, predicate, object)
  #     if not ITEM_SEPARATOR in subject:
  #       s = str(subject).split(CLASS_SEPARATOR)[-1]
  #     else:
  #       s = extract_name_from_class_uri(subject)
  #     p = MYTerms[predicate]
  #     if not ITEM_SEPARATOR in object:
  #       o = str(object).split(CLASS_SEPARATOR)[-1]
  #     else:
  #       o = extract_name_from_class_uri(object)
  #
  #     if predicate in [RDFSTerms["is_defined_by"], RDFSTerms["value"], RDFSTerms["data_type"]]:
  #       triple = o, p, s, -1
  #     else:
  #       triple = s, p, o, 1
  #
  #     tuples_plus.append(triple)
  #
  #   debugging("tuples", tuples_plus)
  #
  #   return tuples_plus
  #
  # def __prepareConjunctiveGraph(self):
  #   conjunctiveGraph = ConjunctiveGraph("Memory")
  #   namespaces = self.dataModel.namespaces
  #   for ns in namespaces:
  #     conjunctiveGraph.bind(ns, namespaces[ns])
  #   for cl in self.dataModel.getClassNamesList():  # class_definition_sequence:
  #     for s, p, o in self.dataModel.GRAPHS[cl].triples((None, None, None)):
  #       # print(s, p, o)
  #       conjunctiveGraph.get_context(namespaces[cl]).add((s, p, o))
  #   return conjunctiveGraph

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

  # def __writeQuadFile(self, conjunctiveGraph, f):
  #   saveBackupFile(f)
  #   inf = open(f, "w")
  #   inf.write(conjunctiveGraph.serialize(format=FILE_FORMAT))
  #   inf.close()
  #   print("written to file ", f)
  #
  # def __makeTree(self, tuples, origin=[], stack=[], items={}):
  #   for q in tuples:
  #     if q not in stack:
  #       s, p, o, dir = q
  #       if s != origin:
  #         if o in items:
  #           item = QTreeWidgetItem(items[o])
  #           item.identifier = o
  #           item.predicate = p
  #           item.setForeground(0, QBRUSHES[p])
  #           stack.append(q)  # (s, p, o))
  #           item.setText(0, s)
  #           items[s] = item
  #           self.__makeTree(tuples, origin=s, stack=stack, items=items)

  # def __renameItemInGraph(self, ID, new_name):
  #   graph = self.dataModel.GRAPHS[self.current_class]
  #   makeURI__ = self.dataModel.makeURI
  #   old_ID = makeURI__(self.current_class, ID)
  #   new_ID = makeURI__(self.current_class, new_name)
  #   for s, p, o in graph.triples((None, None, old_ID)):
  #     # print("debugging -- change triple", s, p, o)
  #     self.dataModel.GRAPHS[self.current_class].remove((s, p, o))
  #     object = new_ID
  #     self.dataModel.GRAPHS[self.current_class].add((s, p, object))
  #   for s, p, o in graph.triples((old_ID, None, None)):
  #     # print("debugging -- change triple", s, p, o)  # add to graph
  #     self.dataModel.GRAPHS[self.current_class].remove((s, p, o))
  #     subject = new_ID
  #     self.dataModel.GRAPHS[self.current_class].add((subject, p, o))
  #   self.__createTree(self.current_class)
  #   self.__ui_state("show_tree")
  #
  # def __makePathName(self, text_ID):  # todo: to remove
  #   p = ROOTCLASS
  #   for i in self.class_path[1:]:
  #     p = p + ".%s" % i
  #   if text_ID not in p:
  #     item_name = text_ID
  #     p = p + ".%s" % item_name
  #   return p
  #
  # def __hasElucidation(self, text_ID, predicate):
  #   return self.__isClass(text_ID) or self.__isSubClass(text_ID) or self.__isValue(predicate)
  #
  # def __addItemToTree(self, internal_object, predicate, internal_subject, parent_item=None):
  #   # generate GUI tree
  #   if not parent_item:
  #     parent_item = self.ui.treeClass.currentItem()
  #   item = QTreeWidgetItem(parent_item)
  #   item.setText(0, internal_object)
  #   item.predicate = predicate
  #   # item.setBackground(0, COLOURS[predicate])# PRIMITIVE_COLOUR)
  #   item.setForeground(0, QBRUSHES[predicate])
  #   self.ui.treeClass.expandAll()
  #   self.changed = True
  #   return item
  #
  # def __permittedClasses(self):
  #   all_linked_classes = self.dataModel.getAllLinkedClasses()
  #   permitted_classes = copy.copy(all_linked_classes)
  #   for c in all_linked_classes:
  #     if (c == self.current_class) or (c in self.class_path):
  #       permitted_classes.remove(c)
  #
  #   return permitted_classes
  #
  # def __addToClassPath(self, addclass):
  #   self.class_path.append(addclass)
  #   self.ui.listClasses.clear()
  #   self.ui.listClasses.addItems(self.class_path)
  #
  # def __removeClassPath(self, Class):
  #   class_path = []
  #   for c in self.class_path:
  #     if Class != c:
  #       class_path.append(c)
  #   self.class_path = class_path
  #   self.ui.listClasses.clear()
  #   self.ui.listClasses.addItems(self.class_path)
  #
  # def __cutClassPath(self, cutclass):
  #   i = self.class_path.index(cutclass)
  #   self.class_path = self.class_path[:i + 1]
  #   self.ui.listClasses.clear()
  #   self.ui.listClasses.addItems(self.class_path)
  #
  # def __shiftClass(self, Class):
  #   # print("debugging ---------------")
  #   self.current_class = Class
  #   self.__createTree(Class)
  #   if Class not in self.class_path:
  #     self.__addToClassPath(Class)
  #   else:
  #     self.__cutClassPath(Class)
  #   self.__ui_state("show_tree")
  #
  # def __getConstraintString(self, prompt, placeholder=""):
  #   forbidden = self.dataModel.getAllNames(self.current_class)
  #   dialog = UI_String(prompt, placeholdertext=placeholder, limiting_list=forbidden)
  #   dialog.exec()
  #   return dialog.getText()
  #
  # def __makeDotGraph(self):
  #   class_names = self.dataModel.getClassNamesList()
  #   triples = set()
  #   for Class in class_names:
  #     for t in self.__prepareTree(Class):
  #       triples.add(t)
  #   pass
  #   print("\n---------------------------------")
  #   file_name = os.path.join(ONTOLOGY_REPOSITORY, self.project_name)
  #   dot = TreePlot(file_name, triples, class_names)
  #   for s, p, o, dir in triples:
  #     debugging("adding node", s, p, o)
  #     subject_type = self.dataModel.what_is_this(self.current_class, s)
  #     object_type = self.dataModel.what_is_this(self.current_class, o)
  #
  #     # type = "other"
  #     try:
  #       type = object_type[0]
  #     except:
  #       type = "other"
  #
  #     # print("s,p,o is:", s, ": ", subject_type,
  #     #       "p: ", p,
  #     #       "o: ", o, object_type,
  #     #       "d: ", dir)
  #     print("s: ", s, subject_type, "      p:", p, "     o: ", o, object_type, "     dir:", dir)
  #     if "class" in object_type:
  #       type = "Class"
  #     if "linked" in object_type:
  #       type = "linked"
  #     if o == "Class":
  #       type = "Class"
  #
  #     if dir == -1:
  #       node = s
  #       if "class" in subject_type:
  #         type = "Class"
  #       if s in PRIMITIVES:
  #         type = "primitive"
  #       elif not subject_type:
  #         type = "other"
  #     else:
  #       if "class" in object_type:
  #         type = "Class"
  #       node = o
  #
  #     # print(node)
  #     # print("adding", node, type)
  #
  #     dot.addNode(node, type)
  #
  #   for s, p, o, dir in triples:
  #     if dir == -1:
  #       dot.addEdge(o, s, p)
  #     else:
  #       dot.addEdge(s, o, p)
  #   pass
  #   # dot.dot.view()
  #   file_path = os.path.join(ONTOLOGY_REPOSITORY, self.project_name + "pdf")
  #   ggg = dot.dot.render(view=True, cleanup=True)
  #   # os.rename(ggg, file_path)
  #
  #   return
