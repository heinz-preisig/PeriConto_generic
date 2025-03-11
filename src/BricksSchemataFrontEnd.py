import os
import sys

from BricksAndTreeSemantics import FILE_FORMAT
from BricksSchemataBackEnd import BackEnd
from Utilities import camelCase
from Utilities import classCase
from resources.radioButtonDialog import RadioButtonDialog

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *

from BricksSchemata_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String

# from PeriConto import debugging
from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from Utilities import debugging

# DEBUGG = False

changed = False


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


class OntobuilderUI(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    # self.ui.tabsBrickTrees.setTabVisible(1,False)

    # self.DEBUGG = True

    roundButton(self.ui.pushOntologyLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushOntologyCreate, "plus", tooltip="create")
    roundButton(self.ui.pushTreeVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushOntologySave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")
    roundButton(self.ui.pushOntologySaveAs, "save_as", tooltip="save with new name")

    roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
    roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
    roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)

    self.interfaceComponents()
    self.backend = BackEnd(self)

    message = {"event": "start"}
    self.backend.processEvent(message)

  def interfaceComponents(self):
    self.window_controls = {
            "maximise": self.ui.pushMaximise,
            "minimise": self.ui.pushMinimise,
            "normal"  : self.ui.pushNormal,
            }

    self.gui_objects = {
            "exit"                          : self.ui.pushExit,
            "brick_tree"                    : self.ui.brickTree,
            "brick_list"                    : self.ui.listBricks,
            "brick_add_item"                : self.ui.pushBrickAddItem,
            "brick_add_primitive"           : self.ui.pushBrickAddPrimitive,
            "brick_change_primitive"        : self.ui.pushBrickChangePrimitive,
            "brick_create"                  : self.ui.pushBrickCreate,
            "brick_item_or_primitive_rename": self.ui.pushBrickItemOrPrimitiveRename,
            "brick_remove"                  : self.ui.pushBrickRemove,
            "brick_remove_item"             : self.ui.pushBrickRemoveItem,
            "brick_rename"                  : self.ui.pushBrickRename,
            "ontology_create"               : self.ui.pushOntologyCreate,
            "ontology_load"                 : self.ui.pushOntologyLoad,
            "ontology_save"                 : self.ui.pushOntologySave,
            "ontology_save_as"              : self.ui.pushOntologySaveAs,
            "tree_visualise"                : self.ui.pushTreeVisualise,
            }

  def setRules(self, rules, primitives):
    self.rules = rules
    self.primitives = primitives

  def setAllNames(self, names):
    self.allNames = names

  def setInterface(self, shows):
    pass

    set_hide = set(self.gui_objects.keys()) - set(shows)
    for hide in set_hide:
      self.gui_objects[hide].hide()
    for show in shows:
      self.gui_objects[show].show()
    pass

  def on_pushOntologyCreate_pressed(self):
    debugging("-- pushOntologyCreate")

    dialog = UI_String("provide new ontology name", placeholdertext="ontology name")
    name = dialog.text
    if name:
      event = "create ontology"
      name = classCase(name)  # rule: class names are upper case
    else:
      event = "start"

    message = {
            "event": event,
            "name" : name
            }
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
    message = {
            "event": "load ontology",
            "name" : project_name
            }
    self.backend.processEvent(message)

  def on_pushOntologySave_pressed(self):
    debugging("-- pushOntologySave")
    if not changed:
      return
    message = {"event": "save"}
    self.backend.processEvent(message)

  def on_pushOntologySaveAs_pressed(self):
    debugging("-- pushOntologySaveAs")
    dialog = UI_String("save as", "new name")
    name = dialog.text
    if name:
      message = {
              "event": "save as",
              "name" : name
              }
      self.backend.processEvent(message)

  def on_pushBrickCreate_pressed(self):
    debugging("-- pushBrickCreate")
    dialog = UI_String("new brick",
                       value=None,
                       placeholdertext="brick name",
                       limiting_list=self.brickList,
                       validator="name_upper")
    name = dialog.text
    if name:
      event = "new brick"
      name = classCase(name)  # rule: class names are upper
    else:
      return
    message = {
            "event": event,
            "name" : name
            }
    self.backend.processEvent(message)

  def on_pushBrickRemove_pressed(self):
    debugging("--pushBrickRemove")
    message = {"event": "remove brick"}
    self.backend.processEvent(message)

  def on_pushBrickAddItem_pressed(self):
    debugging("-- pushBrickAddItem")

    dialog = UI_String("name for the new item",
                       placeholdertext="name -- will be camelised",
                       limiting_list=self.allNames,
                       validator="camel")
    name = dialog.text
    if name:
      event = "add item"
      name = camelCase(name)  # rule items are camel case
    else:
      return
    message = {
            "event": event,
            "name" : name
            }
    self.backend.processEvent(message)

  def askForItemName(self, prompt, existing_names):
    dialog = UI_String(prompt,
                       placeholdertext="item name",
                       limiting_list=existing_names, validator="camel")
    name = dialog.text
    return name

  def on_pushBrickRemoveItem_pressed(self):
    message = {"event": "remove item from brick tree"}  # GUIMessage(event="remove item from brick tree")
    debugging("-- pushBrickRemoveItem")
    self.backend.processEvent(message)

  def on_pushBrickAddPrimitive_pressed(self):
    item = self.ui.brickTree.currentItem()
    parent_name = item.text(0)
    dialog = UI_String("name for the new primitive",
                       placeholdertext="name -- will be camelised",
                       limiting_list=self.allNames,
                       validator="camel")
    primitive_name = dialog.text
    event = None
    if primitive_name:
      primitive_name = camelCase(primitive_name)  # rule items are camel case
      dialog = RadioButtonDialog(self.primitives)
      if dialog.exec():
        primitive = dialog.get_selected_option()
        primitive_type = str(primitive)
        event = "add primitive"
        message = {
                "event": event,
                "name" : primitive_name,
                "type" : primitive_type,
                }
    if event:
      self.backend.processEvent(message)

  def on_pushBrickChangePrimitive_pressed(self):
    debugging("-- pushBrickChangePrimitive")
    dialog = RadioButtonDialog(self.primitives)
    if dialog.exec():
      primitive = dialog.get_selected_option()
      primitive_type = str(primitive)
    message = {
            "event": "change primitive",
            "type" : primitive_type,
            }
    self.backend.processEvent(message)

  def on_pushBrickRename_pressed(self):
    debugging("-- pushBrickRename")
    dialog = UI_String(prompt="new brick name",
                       value=None,
                       placeholdertext="brick name",
                       limiting_list=self.brickList,
                       validator="name_upper")
    new_name = dialog.text
    if new_name:
      event = "rename brick"
      new_name = classCase(new_name)
    else:
      return
    message = {
            "event": event,
            "name" : new_name
            }
    self.backend.processEvent(message)

  def on_pushBrickItemOrPrimitiveRename_pressed(self):
    item = self.ui.brickTree.currentItem()
    type = item.type
    event = "%s rename" % type
    message = {"event": event}
    self.backend.processEvent(message)

  def on_pushTreeVisualise_pressed(self):
    event = "visualise"
    message = {"event": event}
    self.backend.processEvent(message)

    debugging("-- pushTreeVisualise")

  def on_pushMinimise_pressed(self):
    self.showMinimized()

  def on_pushMaximise_pressed(self):
    self.showMaximized()

  def on_pushNormal_pressed(self):
    self.showNormal()

  def on_listBricks_itemClicked(self, item):
    name = item.text()
    debugging("-- listBricks -- item", name)
    event = "selected brick"
    message = {
            "event": event,
            "name" : name
            }
    self.backend.processEvent(message)

  def on_listTrees_itemClicked(self, item):
    name = item.text()
    debugging("-- listTrees -- item", name)
    event = "selected tree"
    message = {
            "event": event,
            "name" : name
            }
    debugging("message:", message)
    self.backend.processEvent(message)

  def on_brickTree_itemClicked(self, item, column):
    name = item.text(column)
    debugging("-- brick tree item %s, column %s" % (name, column))
    selected = item.type
    event = "%s in brick tree selected" % selected
    message = {
            "event": event,
            "name" : name
            }
    debugging("message:", message)
    self.backend.processEvent(message)

  def on_treeTree_itemClicked(self, item, column):
    name = item.text(column)
    debugging("-- tree item %s, column %s" % (name, column))
    selected = item.type
    event = "%s in treeTree selected" % selected
    message = {
            "event": event,
            "name" : name
            }
    self.backend.processEvent(message)

  def showBrickList(self, brickList):
    self.brickList = brickList
    self.ui.listBricks.clear()
    self.ui.listBricks.addItems(brickList)

  def showTreeList(self, treeList):
    self.treeList = treeList

  def showBrickTree(self, tuples, origin):
    widget = self.ui.brickTree
    self.__instantiateTree(origin, tuples, widget)

  def __instantiateTree(self, origin, tuples, widget):
    widget.clear()
    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = origin
    rootItem.setText(0, origin)
    rootItem.setSelected(False)
    rootItem.type = self.rules["is_class"]
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
            item = QTreeWidgetItem(items[o])
            item.type = self.rules[p]
            item.parent_name = o
            item.setForeground(0, QBRUSHES[p])
            stack.append(q)  # (s, p, o))
            if s == "":
              item.setText(0, p)
            else:
              item.setText(0, s)
            items[s] = item
            # debugging("items", s, p, o)
            self.__makeTree(tuples, origin=s, stack=stack, items=items)

  # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s
  def mousePressEvent(self, event, QMouseEvent=None):
    self.dragPos = event.globalPosition().toPoint()

  def mouseMoveEvent(self, event, QMouseEvent=None):
    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
    self.dragPos = event.globalPosition().toPoint()

  def markChanged(self):
    global changed
    changed = True

  def on_pushExit_pressed(self):
    self.closeMe()

  def markSaved(self):
    global changed
    changed = False

  def closeMe(self):
    global changed
    if changed:
      dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
      if dialog == "YES":
        self.on_pushOntologySave_pressed()
      elif dialog == "NO":
        pass
    else:
      pass
    sys.exit()
