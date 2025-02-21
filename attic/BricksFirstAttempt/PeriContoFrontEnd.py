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
    # self["type"] = type
    # self["parent"] = parent


class OntobuilderUI(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    self.ui.tabsBrickTrees.setTabVisible(1,False)

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

    # w = 150
    # h = 25
    # for i in ["add_subclass", "add_primitive", "link_new_class", "link_existing_class"]:
    #   self.gui_objects[i].setFixedSize(w, h)

    self.interfaceComponents()
    self.backend = BackEnd(self)

    message = GUIMessage(event="start")
    self.backend.processEvent(message)
    self.changed = False

  def interfaceComponents(self):
    self.window_controls = {
            "maximise": self.ui.pushMaximise,
            "minimise": self.ui.pushMinimise,
            "normal"  : self.ui.pushNormal,
            }


    self.gui_objects = {
            "exit"                          : self.ui.pushExit,
            "brick_tree"                    : self.ui.brickTree,
            "brick_combo"                   : self.ui.comboBoxTreeSelectBrick,
            "brick_list"                    : self.ui.listBricks,
            "brick_add_item"                : self.ui.pushBrickAddItem,
            "brick_add_primitive"           : self.ui.pushBrickAddPrimitive,
            "brick_create"                  : self.ui.pushBrickCreate,
            "brick_item_or_primitive_rename": self.ui.pushBrickItemOrPrimitiveRename,
            "brick_remove"                  : self.ui.pushBrickRemove,
            "brick_remove_item"             : self.ui.pushBrickRemoveItem,
            "brick_rename"                  : self.ui.pushBrickRename,
            "ontology_create"               : self.ui.pushOntologyCreate,
            "ontology_load"                 : self.ui.pushOntologyLoad,
            "ontology_save"                 : self.ui.pushOntologySave,
            "ontology_save_as"              : self.ui.pushOntologySaveAs,
            "tree_create"                   : self.ui.pushTreeCreate,
            "tree_delete"                   : self.ui.pushDeleteTree,
            "tree_combo_select_brick"       : self.ui.comboBoxTreeSelectBrick,
            "tree_instantiate"              : self.ui.pushTreeInstantiate,
            "tree_list"                     : self.ui.listTrees,
            "tree_link_existing_class"      : self.ui.pushTreeLinkExistingClass,
            "tree_remove_class_link"        : self.ui.pushTreeRemoveClassLink,
            "tree_visualise"                : self.ui.pushTreeVisualise,
            "tabs"                          : self.ui.tabsBrickTrees,
            "tree_tree"                     : self.ui.treeTree,
            }

  def setRules(self, rules):
    self.rules = rules

  def setTabVisible(self):
    debugging("enable taps")
    self.ui.tabsBrickTrees.setTabVisible(1, True)

  def setInterface(self, shows):
    pass

    set_hide = set(self.gui_objects.keys()) - set(shows)
    for hide in set_hide:
      self.gui_objects[hide].hide()
    for show in shows:
      self.gui_objects[show].show()
    # debugging("shows")
    # debugging(shows)
    # debugging("\nhides")
    # debugging(set_hide)
    pass

  def on_pushOntologyCreate_pressed(self):
    debugging("-- pushOntologyCreate")

    dialog = UI_String("provide new ontology name", placeholdertext="ontology name")
    # dialog.exec()
    name = dialog.text
    if name:
      event = "create ontology"
      name = name.upper()
    else:
      event = "start"

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
    dialog = UI_String("save as", "new name")
    name = dialog.text
    if name:
      message = GUIMessage(event=event, name=name)
      self.backend.processEvent(message)

  def on_pushBrickCreate_pressed(self):
    debugging("-- pushBrickCreate")
    dialog = UI_String("new brick", "brick name", self.brickList)
    # dialog.exec()
    name = dialog.text
    if name:
      event = "new brick"
      name = name.upper()
    else:
      event = None
    message = GUIMessage(event=event, name=name)
    self.backend.processEvent(message)

  def on_pushBrickRemove_pressed(self):
    message = GUIMessage()
    debugging("--pushBrickRemove  -- not implemented")

  def on_pushBrickAddItem_pressed(self):
    debugging("-- pushBrickAddItem")
    event = "asks for adding an item"
    message = GUIMessage(event=event)
    self.backend.processEvent(message)

  def askForItemName(self, prompt, existing_names):
    dialog = UI_String(prompt,
                       placeholdertext="item name",
                       limiting_list=existing_names)
    # dialog.exec()
    name = dialog.text
    return name

  def askForPrimitiveType(self, primitives):
    # self.ui.comboBoxPrimitives.show()
    dialog = UI_ComboDialog("select primitive", primitives)
    primitive = dialog.getSelection()
    return primitive

  # def setPrimitives(self, PRIMITIVES):
  #   self.ui.comboBoxPrimitives.clear()
  #   # self.ui.comboBoxPrimitives.addItems(PRIMITIVES)

  def on_pushBrickRemoveItem_pressed(self):
    message = GUIMessage(event="remove item from brick tree")
    debugging("-- pushBrickRemoveItem")
    self.backend.processEvent(message)

  def on_pushBrickAddPrimitive_pressed(self):
    item = self.ui.brickTree.currentItem()
    name = item.text(0)
    # parent_name = item.parent_name
    debugging("-- pushBrickAddPrimitive")
    event = "ask for adding a primitive"
    message = GUIMessage(event=event,
                         name=name,
                         # type=item.predicate,
                         # parent=parent_name
                         )
    self.backend.processEvent(message)

  def on_pushBrickRename_pressed(self):
    event = "rename brick"
    message = GUIMessage(event= event)
    self.backend.processEvent(message)
    debugging("-- pushBrickRename")

  def on_pushBrickItemOrPrimitiveRename_pressed(self):
    item = self.ui.brickTree.currentItem()
    type = item.type
    name = item.text(0)
    event = "%s rename"%type
    message = GUIMessage(event=event)
    self.backend.processEvent(message)

  def on_pushTreeCreate_pressed(self):
    debugging("-- pushTreeCreate")
    dialog = UI_String("new tree",
                       "tree name",
                       self.brickList)
    # dialog.exec()
    name = dialog.text
    if name:
      event = "new tree"
    else:
      event = None
    message = GUIMessage(event=event, name=name.upper())
    self.backend.processEvent(message)

  def on_pushDeleteTree_pressed(self):
    debugging("-- pushDeleteTree")

  def on_pushTreeLinkExistingClass_pressed(self):
    debugging("-- pushTreeLinkExistingClass")

  def on_pushTreeRemoveClassLink_pressed(self):
    debugging("-- pushTreeRemoveClassLink")

  def on_pushTreeInstantiate_pressed(self):
    debugging("-- pushTreeInstantiate")

  def on_pushTreeVisualise_pressed(self):
    event = "visualise"
    message = GUIMessage(event=event)
    self.backend.processEvent(message)

    debugging("-- pushTreeVisualise")

  def on_pushMinimise_pressed(self):
    self.showMinimized()

  def on_pushMaximise_pressed(self):
    self.showMaximized()

  def on_pushNormal_pressed(self):
    self.showNormal()

  def on_tabsBrickTrees_currentChanged(self, index):
    # debugging("-- tabWidgetLists -- index", index)
    tab = self.ui.tabsBrickTrees.tabText(index)
    event = "tab changed to %s"%tab
    message = GUIMessage(event=event, name=tab)
    debugging("tab message",message)

  def on_listBricks_itemClicked(self, item):
    name = item.text()
    debugging("-- listBricks -- item", name)
    event = "selected brick"
    message = GUIMessage(event=event, name=name)
    self.backend.processEvent(message)

  def on_listTrees_itemClicked(self, item):
    name = item.text()
    debugging("-- listTrees -- item", name)
    event = "selected tree"
    message = GUIMessage(event = event, name=name)
    debugging("message:", message)
    self.backend.processEvent(message)

  def on_treeTree_itemClicked(self, item):
    name = item.text()
    event= "selected node in treeTree"
    message = GUIMessage(event=event, name=name)
    debugging("--tree_tree_item:", message)
    self.backend.processEvent(message)

  def on_brickTree_itemClicked(self, item, column):
    name = item.text(column)
    debugging("-- brick tree item %s, column %s" % (name, column))
    selected = item.type
    event = "%s in brick tree selected"%selected
    message = GUIMessage(event=event,
                         name=name,
                         # type=item.predicate,
                         # parent=item.parent_name
                         )
    debugging("message:", message)
    self.backend.processEvent(message)

  def on_treeTree_itemClicked(self, item, column):
    name = item.text(column)
    debugging("-- tree item %s, column %s" % (name, column))
    selected = item.type
    event = "%s in treeTree selected"%selected
    message = GUIMessage(event=event,
                         name=name,
                         # type=item.predicate,
                         # parent=item.parent_name
                         )
    debugging("message:", message)
    self.backend.processEvent(message)

  def showBrickList(self, brickList):
    self.brickList = brickList
    self.ui.listBricks.clear()
    self.ui.listBricks.addItems(brickList)
    self.ui.comboBoxTreeSelectBrick.clear()
    self.ui.comboBoxTreeSelectBrick.addItems(brickList)

  def showTreeList(self, treeList):
    self.treeList = treeList
    self.ui.listTrees.clear()
    self.ui.listTrees.addItems(treeList)

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
    rootItem.type = self.rules["is_class"]
    # rootItem.parent_name = "Class"
    # rootItem.predicate = "is_class"
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
            item.type = self.rules[p]
            item.parent_name = o
            # item.predicate = p
            item.setForeground(0, QBRUSHES[p])
            stack.append(q)  # (s, p, o))
            if s == "":
              item.setText(0,p)
            else:
              item.setText(0, s)
            items[s] = item
            debugging("items", s,p,o)
            self.__makeTree(tuples, origin=s, stack=stack, items=items)

  def putTreeList(self, tree_list):
    self.ui.listTrees.clear()
    self.ui.listTrees.addItems(tree_list)

  def putBricksListForTree(self, brick_list):
    self.ui.comboBoxTreeSelectBrick.clear()
    self.ui.comboBoxTreeSelectBrick.addItems(brick_list)

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

