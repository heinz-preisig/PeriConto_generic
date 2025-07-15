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
"add item"
"rename item"
"remove item"
"link"
"reduce"
"visualise"
"selected tree"
"got primitive"
"%s in treeTree selected" % type
"item in treeTree selected can be linked"
"do_nothing"


"""
import copy
import os
import sys

from BricksAndTreeSemantics import FILE_FORMAT
from TreeSchemataBackEnd import BackEnd
from Utilities import classCase, breadth_first_iter, depth_first_iter


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

DEBUGG = False

# global expanded_state
# global tree_name
# global changed
expanded_state = {}
tree_name = None
changed = False

COLOURS = {
        "Class"         : QtGui.QColor(0, 199, 255),
        "ROOT"         : QtGui.QColor(0, 199, 255),
        "is_member"    : QtGui.QColor(0, 0, 0, 255),
        "member"       : QtGui.QColor(0, 0, 0, 255),
        "is_defined_by": QtGui.QColor(255, 100, 5, 255),
        "isDefinedBy"  : QtGui.QColor(255, 100, 5, 255),
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


def PrintGraph(graph):
  print("graph")
  for s, p, o in graph.triples((None, None, None)):
    print(s, p, o)
  print("end graph")

class DebugTreeWidgetItem(QTreeWidgetItem):
  def __setattr__(self, name, value):
    if name == 'node_type':
      print(f"Setting node_type for item '{self.text(0)}' from {getattr(self, 'node_type', 'None')} to {value}")
    super().__setattr__(name, value)

class OntobuilderUI(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    # self.ui.tabsBrickTrees.setTabVisible(1,False)

    roundButton(self.ui.pushOntologyLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushTreeVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushOntologySave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")
    roundButton(self.ui.pushOntologySaveAs, "save_as", tooltip="save with new name")

    roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
    roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
    roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)

    self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)

    self.interfaceComponents()
    self.backend = BackEnd(self)

    message = {"event": "start"}
    self.backend.processEvent(message)
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
            # "item_rename"             : self.ui.pushItemRename,
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
    """
    Updates the interface by displaying the specified GUI components
    and hiding all others.

    Args:
        shows (list): A list of keys corresponding to the GUI components
                      that should be shown.

    The method iterates through the GUI components, hiding those not
    in the 'shows' list and displaying those that are.
    """
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
    project_name = dialog.text
    if project_name:
      message = {
              "event"       : "save as",
              "project_name": project_name
              }
      self.ui.labelProject.setText(project_name)
      self.markSaved()
      self.backend.processEvent(message)

  def on_pushTreeCreate_pressed(self):
    global tree_name
    debugging("-- pushTreeCreate")
    dialog = UI_stringSelector("select brick",
                               self.brickList)
    brick_name = dialog.selection
    if brick_name:
      forbidden = self.treeList + self.brickList
      dialog = UI_String("tree name", limiting_list=forbidden, validator="name_upper")
      tree_name = dialog.text
      if not tree_name:
        return
    else:
      return
    # tree_name = brick_name
    message = {
            "event"     : "new tree",
            "tree_name" : classCase(tree_name),  # .upper(),
            "brick_name": brick_name  # classCase(tree_name) # brick_name
            }
    self.backend.processEvent(message)

  def on_pushTreeRename_pressed(self):
    global tree_name
    existing_names = self.treeList + list(self.existing_names)
    dialog = UI_String("new_tree name", limiting_list=existing_names, validator="name_upper")
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
    existing_names = self.treeList + list(self.existing_names)
    item_name = self.askForItemName("item name", existing_names)
    if not item_name:
      return
    message = {
            "event"    : "add item",
            "item_name": item_name
            }
    self.backend.processEvent(message)

  # def on_pushItemRename_pressed(self):Note: consider using the path to inhibit duplicated names, terrible complicated -- abandon!
  #   debugging("-- pushItemRename")
  #   current_item = self.ui.treeTree.currentItem()
  #   leave_item = self.__findLeaf(current_item)
  #   path_to_leave = self.__makePath(leave_item)
  #   if not path_to_leave:
  #     return
  #   item_name = self.askForItemName("item name", path_to_leave) #self.existing_names)
  #   if not item_name:
  #     return
  #   message = {
  #           "event"    : "rename item",
  #           "item_name": item_name,
  #           "path_to_leave": path_to_leave,
  #           }
  #   self.backend.processEvent(message)

  def on_pushRemoveItem_pressed(self):
    debugging("-- pushRemoveItem")

    current_item = self.ui.treeTree.currentItem()
    leave_item = self.__findLeaf(current_item)
    path_to_leave = self.__makePath(leave_item)
    if "instance" in path_to_leave[0]:
      makeMessageBox("this path has a leave with an instance -- it cannot be removed", buttons=["OK"])
      return

    item_name = current_item.text(0)
    parent_name = current_item.parent().text(0)


    message = {
            "event": "remove item",
            "item_name" : item_name,
            "parent_name": parent_name,
            }
    self.backend.processEvent(message)

  def on_pushTreeLinkExistingClass_pressed(self):
    # print("-- pushTreeLinkExistingClass")
    current_item = self.ui.treeTree.currentItem()
    brick_list = copy.copy(self.brickList)
    path = self.__makePath(current_item)
    for i in path:  # RULE: make sure that no name is repeated in any path
      if i in brick_list:
        brick_list.remove(i)

    if not current_item:
      return
    dialog = UI_stringSelector("select brick",
                               brick_list)
    brick_name = dialog.selection
    if brick_name == "":
      return

    message = {
            "event"     : "link",
            "brick_name": brick_name,
            "path"      : path,
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
    type = item.node_type
    print("name, type:", name, type)
    if type != "Class":
      parent_name = item.parent().text(0)
    else:
      parent_name = None
    linkpoint = (item.childCount() == 0) and (type == self.rules["is_member"])
    debugging("item count", item.childCount(), linkpoint)
    debugging("-- tree item %s, column %s" % (name, column))
    if not linkpoint:
      if type in self.primitives:
        x = self.__makePath(item)
        # print(x)
        value = None
        instance = None
        if name not in self.primitives:
          if ":" in name:
            instance, value = name.split(":")
          else:
            instance = name
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
          value = "undefined"
        instance = instance + ":" + value
        message = {
                "event"      : "got primitive",
                "value"      : instance,
                "type"       : type,
                "parent_name": parent_name,
                "path"       : x,
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

  def __makePath(self, item):
    i = item
    x = []
    while i.parent():
      x.append(i.text(0))
      i = i.parent()
    x.append(i.text(0))
    return x

  def __findLeaf(self, item):
    while item.childCount() != 0:
      for i in range(item.childCount()):
        item = item.child(i)
    return item

  def showTreeList(self, treeList):
    self.treeList = treeList
    self.ui.listTrees.clear()
    self.ui.listTrees.addItems(treeList)


  def showNewNewTreeTree(self, root_name, paths, properties, leaves, instances):
    widget = self.ui.treeTree
    # PrintGraph(graph)

    self.existing_names = set()

    # _, name = root.split("#")
    count_children = 0
    widget.clear()
    # rootItem = DebugTreeWidgetItem(widget)
    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = root_name
    rootItem.setText(0, root_name)
    rootItem.setSelected(False)
    type = self.rules["is_class"]
    rootItem.node_type = type
    rootItem.count = count_children
    rootItem.id = 1
    widget.addTopLevelItem(rootItem)
    rootItem.count = 0
    self.treetop = widget.invisibleRootItem()
    self.current_class = root_name
    node_id = 0
    items = {node_id: rootItem}
    self.existing_names.add(root_name)
    pass


    for leave in leaves:
      for path in paths[leave]:
        parent_item = rootItem
        current_path = []
        
        # Build the path from leaf to root
        for i in reversed(path[:-1]):
          if "instance" in i:
            instance = i.split(":")[0]
            try:
              node_text = instance+":"+ instances[tree_name][instance]["value"]
            except:
              pass
          else:
            node_text = i
          current_path.append((parent_item, node_text))
          
          # Find or create the child item
          found = None
          for child_idx in range(parent_item.childCount()):
            child = parent_item.child(child_idx)
            if child.text(0) == node_text:
              found = child
              break
              
          if found is None:
            # found = DebugTreeWidgetItem(parent_item)
            found = QTreeWidgetItem(parent_item)
            found.setText(0, node_text)
            node_id += 1
            items[node_id] = found
            
            # Set the node type for new items
            if "undefined" not in node_text:
              node_type = properties[leave][0].get(node_text.split(":")[0], "unknown")
              # print(f"Creating new node '{node_text}' with type: {node_type}")
              found.node_type = node_type
            else:
              node_type = properties[leave][0][instance]
              print(f"Creating new undefined node with type from {path[0]}: {node_type}")
              found.node_type = node_type

            if node_type == "unknown":
              print(f">>> Node type for '{node_text}' is still unknown")
          parent_item = found
          
        # The last node in the path is the leaf
        if path and len(path) > 1:
          node_text = path[-1].split('#')[-1] if '#' in path[-1] else path[-1]
          # For leaf nodes, use the first property in the path if node_text is undefined
          if node_text == "undefined" and path[0] in properties[leave][0]:
            node_type = properties[leave][0][path[0]]
            print(f"Setting undefined leaf node type using {path[0]}: {node_type}")
            parent_item.node_type = node_type
          elif node_text in properties[leave][0]:
            node_type = properties[leave][0][node_text]
            print(f"Setting leaf node '{node_text}' type to: {node_type}")
            parent_item.node_type = node_type

    for i in items:
      node_type = items[i].node_type
      items[i].setForeground(0, QBRUSHES[node_type])
      print(">>> node",items[i].text(0), node_type)

    widget.show()
    widget.expandAll()
    # self.__ui_state("show_tree")

    try:
      self.restore_expanded_state()
    except:
      pass

  # def showNewTreeTree(self, graph, root, instances):
  #   pass
  #   widget = self.ui.treeTree
  #   # PrintGraph(graph)
  #
  #   self.existing_names = set()
  #
  #   _, name = root.split("#")
  #   count_children = 0
  #   widget.clear()
  #   rootItem = QTreeWidgetItem(widget)
  #   widget.setColumnCount(1)
  #   rootItem.root = name
  #   rootItem.setText(0, name)
  #   rootItem.setSelected(False)
  #   rootItem.node_type = self.rules["is_class"]
  #   rootItem.count = count_children
  #   rootItem.id = 1
  #   widget.addTopLevelItem(rootItem)
  #   self.treetop = widget.invisibleRootItem()
  #   self.current_class = name
  #   items = {1: rootItem}
  #   self.existing_names.add(name)
  #
  #   for depth, node, current_branch, parent, predicate, node_id, parent_id in depth_first_iter(graph, root):
  #     # print(root)
  #     print(depth, node, current_branch, parent, predicate, node_id, parent_id)
  #     if node != root:
  #       try:
  #         _, name = node.split("#")
  #       except:
  #         name = str(node)
  #       self.existing_names.add(name)
  #       _, parent_name = parent.split("#")
  #       parent_item = items[parent_id]  # items[parent_name]
  #       items[node_id] = QTreeWidgetItem(parent_item)
  #       # print("made item")
  #       items[node_id].count = 0
  #       items[parent_id].count += 1
  #       _, node_type = predicate.split("#")
  #       items[node_id].node_type = node_type
  #       if "instance" in name:
  #         instance_ID, number = name.split(":")
  #         path = instances[tree_name][instance_ID]
  #         x = self.__makePath(items[node_id])
  #         x[0] = name
  #         # for i in instances[tree_name]:
  #         #   path = instances[tree_name][i]
  #         if path != x:
  #           print("\ninstance", instance_ID)
  #           print(depth, node, current_branch, parent, predicate, node_id, parent_id)
  #           print("path", path)
  #           print("x   ", x)
  #         else:
  #           print("\nOk instance", instance_ID)
  #         # print("name", name)
  #         # print("instance", instance)
  #         if path == x:  # (path[1:] == x[1:]) and (instance == name):
  #           items[node_id].setText(0, name)
  #       else:
  #         items[node_id].setText(0, name)
  #
  #       if items[node_id].text(0) == "":
  #         # print(">>>> found obsolete item", x, "parent_path", x_p)
  #         # Note: this item was generated but not named -- couldn't find another solution
  #         parent_item.removeChild(items[node_id])
  #
  #       try:
  #         items[node_id].setForeground(0, QBRUSHES[node_type])
  #       except:
  #         pass
  #
  #   widget.show()
  #   widget.expandAll()
  #   # widget.collapseAll()
  #   try:
  #     self.restore_expanded_state()
  #   except:
  #     pass

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
