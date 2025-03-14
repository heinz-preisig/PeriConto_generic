"""
front end for tree construction

messages:
"start"
"load ontology"
"save"
"save as"
"new tree"
"rename tree"
"copy tree"
"delete tree"
"rename item"
"remove item"
"add item"
"link"
"reduce"
"visualise"
"selected tree"
"got primitive"
"%s in treeTree selected" % type
"item in treeTree selected can be linked"
"do_nothing"


"""
import os
import sys
# import timeit
import time

from BricksAndTreeSemantics import FILE_FORMAT
from TreeSchemataBackEnd import BackEnd
from Utilities import classCase

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *

from TreeSchemata_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String
from resources.ui_single_list_selector_impl import UI_stringSelector
from resources.radioButtonDialog import RadioButtonDialog
from Utilities import debugging

from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY

# DEBUGG = False

# global expanded_state
# global tree_name
# global changed
expanded_state = {}
tree_name = None
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
    # roundButton(self.ui.pushOntologyCreate, "plus", tooltip="create")
    roundButton(self.ui.pushTreeVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushOntologySave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")
    roundButton(self.ui.pushOntologySaveAs, "save_as", tooltip="save with new name")
    # roundButton(self.ui.pushBricks, "bricks", tooltip="building bricks mode")
    # roundButton(self.ui.pushTree, "build_tree", tooltip="building tree mode")
    # roundButton(self.ui.pushInstantiate, "instantiate_tree", tooltip="instantiate tree mode")

    roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
    roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
    roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)
    # roundButton(self.ui.pushExit, "reject", tooltip="exit", mysize=35)

    self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)

    self.interfaceComponents()
    self.backend = BackEnd(self)

    message = {"event": "start"}
    self.backend.processEvent(message)
    # self.expanded_state = {}
    self.treetop = {}

  def interfaceComponents(self):
    self.window_controls = {
            "maximise": self.ui.pushMaximise,
            "minimise": self.ui.pushMinimise,
            "normal"  : self.ui.pushNormal,
            }

    self.gui_objects = {
            "exit"                    : self.ui.pushExit,
            "ontology_load"           : self.ui.pushOntologyLoad,
            "ontology_save"           : self.ui.pushOntologySave,
            "ontology_save_as"        : self.ui.pushOntologySaveAs,
            "tree_create"             : self.ui.pushTreeCreate,
            "tree_delete"             : self.ui.pushTreeDelete,
            "tree_copy"               : self.ui.pushTreeCopy,
            "tree_rename"             : self.ui.pushTreeRename,
            "item_insert"             : self.ui.pushTreeAddItem,
            "item_rename"             : self.ui.pushItemRename,
            "remove_item"             : self.ui.pushRemoveItem,
            "tree_reduce"             : self.ui.pushTreeReduce,
            "tree_list"               : self.ui.listTrees,
            "tree_link_existing_class": self.ui.pushTreeLinkExistingClass,
            "tree_visualise"          : self.ui.pushTreeVisualise,
            "tree_tree"               : self.ui.treeTree,
            }

  def setRules(self, rules, primitives):
    self.rules = rules
    self.primitives = primitives

  def setInterface(self, shows):
    pass

    set_hide = set(self.gui_objects.keys()) - set(shows)
    for hide in set_hide:
      self.gui_objects[hide].hide()
    for show in shows:
      self.gui_objects[show].show()
    pass

  def askForItemName(self, prompt, existing_names):
    dialog = UI_String(prompt,
                       placeholdertext="item name",
                       limiting_list=existing_names, validator="camel")
    # dialog.exec()
    name = dialog.text
    return name

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
            "event"       : "load ontology",
            "project_name": project_name
            }
    self.backend.processEvent(message)
    self.ui.labelProject.setText(project_name)
    # self.ui.statusbar.showMessage("loading file")

  def on_pushOntologySave_pressed(self):
    global changed
    if not changed:
      return
    debugging("-- pushOntologySave")
    message = {"event": "save"}
    self.backend.processEvent(message)
    self.markSaved()

  def on_pushOntologySaveAs_pressed(self):
    debugging("-- pushOntologySaveAs")
    dialog = UI_String("save as", "new name")
    name = dialog.text
    if name:
      message = {
              "event"       : "save as",
              "project_name": name
              }
      self.backend.processEvent(message)
      self.markSaved()

  def on_pushTreeCreate_pressed(self):
    global tree_name
    debugging("-- pushTreeCreate")
    dialog = UI_stringSelector("select brick",
                               self.brickList)
    # dialog.exec()
    brick_name = dialog.selection
    if brick_name:
      dialog = UI_String("tree name", limiting_list=self.treeList, validator="name_upper")
      tree_name = dialog.text
      if not tree_name:
        return
    else:
      return
    message = {
            "event"     : "new tree",
            "tree_name" : classCase(tree_name),  # .upper(),
            "brick_name": brick_name
            }
    self.backend.processEvent(message)

  def on_pushTreeRename_pressed(self):
    global tree_name
    dialog = UI_String("new_tree name", limiting_list=self.treeList, validator="name_upper")
    tree_name = dialog.text
    if not tree_name:
      return
    else:
      message = {
              "event"    : "rename tree",
              "tree_name": classCase(tree_name)
              }  # .upper()}
      self.backend.processEvent(message)

  def on_pushTreeCopy_pressed(self):
    global tree_name
    dialog = UI_String("name for the copy", limiting_list=self.treeList, validator="name_upper")
    tree_name = dialog.text
    if not tree_name:
      return
    else:
      message = {
              "event"    : "copy tree",
              "tree_name": classCase(tree_name)
              }  # .upper()}
      self.backend.processEvent(message)

  def on_pushTreeDelete_pressed(self):
    debugging("-- pushDeleteTree")
    message = {"event": "delete tree"}
    self.backend.processEvent(message)

  def on_pushTreeAddItem_pressed(self):
    debugging("-- pushBrickAddItem")
    item_name = self.askForItemName("item name", self.existing_item_names)
    if not item_name:
      return
    message = {
            "event"    : "add item",
            "item_name": item_name
            }
    self.backend.processEvent(message)

  def on_pushItemRename_pressed(self):
    debugging("-- pushItemRename")
    item_name = self.askForItemName("item name", self.existing_item_names)
    if not item_name:
      return
    message = {
            "event"    : "rename item",
            "item_name": item_name
            }
    self.backend.processEvent(message)

  def on_pushRemoveItem_pressed(self):
    debugging("-- pushRemoveItem")
    message = {
            "event": "remove item",
            }
    self.backend.processEvent(message)

  def on_pushTreeLinkExistingClass_pressed(self):
    print("-- pushTreeLinkExistingClass")
    dialog = UI_stringSelector("select brick",
                               self.brickList)
    brick_name = dialog.selection
    message = {
            "event"     : "link",
            "brick_name": brick_name,
            }
    self.backend.processEvent(message)

  def on_pushTreeReduce_pressed(self):
    debugging("-- pushTreeInstantiate")
    message = {"event": "reduce"}
    self.backend.processEvent(message)

  def on_pushTreeVisualise_pressed(self):
    message = {"event": "visualise"}
    self.backend.processEvent(message)

    debugging("-- pushTreeVisualise")

  def on_pushMinimise_pressed(self):
    self.showMinimized()

  def on_pushMaximise_pressed(self):
    self.showMaximized()

  def on_pushNormal_pressed(self):
    self.showNormal()

  def on_listTrees_itemClicked(self, item):
    global tree_name
    global expanded_state
    tree_name = item.text()
    debugging("-- listTrees -- item", tree_name)
    message = {
            "event"    : "selected tree",
            "tree_name": tree_name
            }
    debugging("message:", message)
    if tree_name not in expanded_state:
      expanded_state[tree_name] = {}
    self.backend.processEvent(message)

  def on_treeTree_itemClicked(self, item, column):
    name = item.text(column)
    self.ui.treeTree.expandItem(item)
    self.save_expanded_state()
    type = item.type
    if type != "Class":
      parent_name = item.parent().text(0)
    else:
      parent_name = None
    linkpoint = (item.count == 0) and (type == self.rules["is_member"])
    debugging("item count", item.count, linkpoint)
    debugging("-- tree item %s, column %s" % (name, column))
    event = "do_nothing"
    if not linkpoint:
      if type in self.primitives:
        value = None
        if name not in self.primitives:
          value = name
        if type == "boolean":
          dialog = RadioButtonDialog(["True", "False"])
          if dialog.exec():
            value = dialog.get_selected_option()
          else:
            value = ""
        else:
          dialog = UI_String("provide %s" % type,
                           value=value,
                           placeholdertext=type,
                           validator=type)
          value = dialog.text
        if not value:
          value = ""
        message = {
                "event"      : "got primitive",
                "value"      : value,
                "type"       : type,
                "parent_name": parent_name,
                }
        self.backend.processEvent(message)
        return

      else:
        event = "%s in treeTree selected" % type
    else:
      event = "item in treeTree selected can be linked"
    message = {
            "event"         : event,
            "tree_item_name": name,
            "item_type"     : type
            }
    debugging("message:", message)
    self.backend.processEvent(message)



  def showTreeList(self, treeList):
    self.treeList = treeList
    self.ui.listTrees.clear()
    self.ui.listTrees.addItems(treeList)

  def showTreeTree(self, tuples, origin, existing_item_names):
    self.existing_item_names = existing_item_names
    widget = self.ui.treeTree
    self.__instantiateTree(origin, tuples, widget)
    try:
      self.restore_expanded_state()
    except:
      pass

  def __instantiateTree(self, origin, tuples, widget):
    widget.clear()
    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = origin
    rootItem.setText(0, origin)
    rootItem.setSelected(False)
    rootItem.type = self.rules["is_class"]
    rootItem.count = 0
    widget.addTopLevelItem(rootItem)
    self.treetop = widget.invisibleRootItem()

    self.current_class = origin
    self.__makeTree(tuples, origin=origin, stack=[], items={origin: rootItem})
    widget.show()
    # widget.expandAll()
    widget.collapseAll()

  def __makeTree(self, tuples, origin=[], stack=[], items={}):
    for q in tuples:
      if q not in stack:
        s, p, o, dir = q
        if s != origin:
          if o in items:
            # if s != "":
            item = QTreeWidgetItem(items[o])
            item.count = 0
            item.type = self.rules[p]
            item.parent_name = o
            item.setForeground(0, QBRUSHES[p])
            stack.append(q)  # (s, p, o))
            if s == "":
              item.setText(0, p)
            else:
              item.setText(0, s)
            items[s] = item
            try:
              items[o].count += 1
            except:
              pass

            debugging("items", s, p, o)
            self.__makeTree(tuples, origin=s, stack=stack, items=items)

  def putTreeList(self, tree_list):
    self.treeList = tree_list
    self.ui.listTrees.clear()
    self.ui.listTrees.addItems(tree_list)

  def putBricksListForTree(self, brick_list):
    self.brickList = brick_list

  def save_expanded_state(self):
    """Stores the expanded state of all items in the tree."""
    expanded_state = {}
    # self._iterate_tree(self.ui.treeTree.invisibleRootItem(), save=True)
    self._iterate_tree(self.treetop, save=True)

  def restore_expanded_state(self):
    """Restores the expanded state of all items in the tree."""
    # self._iterate_tree(self.ui.treeTree.invisibleRootItem(), save=False)
    self._iterate_tree(self.treetop, save=False)

  def _iterate_tree(self, item, save=True):
    global expanded_state
    global tree_name

    """Helper function to iterate through tree items recursively."""
    for i in range(item.childCount()):
      child = item.child(i)
      key = child.text(0)  # Using item text as a unique key

      if save:
        expanded_state[tree_name][key] = child.isExpanded()
      else:
        if key in expanded_state[tree_name]:
          child.setExpanded(expanded_state[tree_name][key])

      self._iterate_tree(child, save)

  # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s
  def mousePressEvent(self, event, QMouseEvent=None):
    self.dragPos = event.globalPosition().toPoint()

  def mouseMoveEvent(self, event, QMouseEvent=None):
    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
    self.dragPos = event.globalPosition().toPoint()

  def markChanged(self):
    global changed
    changed = True
    self.signalButton.changeIcon("LED_red")
    self.ui.statusbar.showMessage("modified")

  def on_pushExit_pressed(self):
    self.closeMe()

  def markSaved(self):
    global changed
    changed = False
    self.signalButton.changeIcon("LED_green")
    self.ui.statusbar.showMessage("up to date")

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
