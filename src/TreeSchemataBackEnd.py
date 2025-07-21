import os
import subprocess
import sys
import time

from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import PRIMITIVES
from BricksAndTreeSemantics import RULES
from DataModelNoBrickNumbers import DataModel
from TreeAutomaton import UI_state
from Utilities import TreePlot
from Utilities import camelCase
from Utilities import debugging
from resources.pop_up_message_box import makeMessageBox

TIMING = False
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])


class BackEnd:
  def __init__(self, frontEnd):
    self.memory = {
            "brick"            : None,
            "item"             : None,
            "tree schema"      : None,
            "tree instantiated": None,
            "new tree"         : False
            }

    self.state = "start"
    self.previousEvent = "start"

    self.UI_state = UI_state

    self.frontEnd = frontEnd
    self.rules = RULES
    self.frontEnd.setRules(RULES, PRIMITIVES)
    self.primitive_counter = 0

    self.project_name = None
    self.dataModel = None

  def processEvent(self, message):
    if TIMING: start = time.time()
    debugging(">>>> message ", message)
    event = message["event"]
    # self.fail = False
    for a in self.UI_state[event]["action"]:
      if a == "addItem":
        self.addItem(message)
      elif a == "addLink":
        self.addLink(message)
      elif a == "copyTree":
        self.copyTree(message)
      elif a == "deleteTree":
        self.deleteTree(message)
      elif a == "extractInstance":
        self.extractInstance(message)
      elif a == "showTree":
        self.showTree(message)
      elif a == "instantiatePrimitive":
        self.instantiatePrimitive(message)
      elif a == "loadOntology":  #
        self.loadOntology(message)
      elif a == "markChanged":
        self.markChanged(message)
      elif a == "newTree":
        self.newTree(message)
      elif a == "putBricksListForTree":
        self.putBricksListForTree(message)
      elif a == "putTreeList":
        self.putTreeList(message)
      elif a == "removeItem":
        self.removeItem(message)
      # elif a == "renameItem":
      #   self.renameItem(message)
      elif a == "saveTreeWithNewName":
        self.saveTreeWithNewName(message)
      elif a == "renameTree":
        self.renameTree(message)
      elif a == "saveTrees":
        self.saveTrees(message)
      elif a == "visualise":
        self.visualise(message)
      else:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> oops no such command", a)

    if len(self.UI_state[event]["show"]) > 0:
      if self.UI_state[event]["show"][0] == "do_nothing":
        return
    ui_state = self.UI_state[event]
    self.frontEnd.setInterface(ui_state["show"])
    self.previousEvent = event

    self.memory.update(message)
    if TIMING: print("processing time", time.time() - start)

  def loadOntology(self, message):
    name = message["project_name"]
    self.project_name = name
    self.dataModel = DataModel(name)
    self.dataModel.loadFromFile()
    pass

  def markChanged(self, message):
    self.frontEnd.markChanged()

  def saveTreeWithNewName(self, message):
    project_name = message["project_name"]
    self.dataModel.saveBricksTreesAndInstances(project_name)
    self.project_name = project_name

  def copyTree(self, message):
    """
    copy a tree with a new name
    """
    tree_to_be_copied_name = self.memory["tree_name"]
    tree_name = message["tree_name"]
    self.dataModel.copyTree(tree_to_be_copied_name, tree_name)
    self.memory["tree_name"] = tree_name
    pass

  def addItem(self, message):
    tree_item_name = self.memory["tree_item_name"]
    item_name = camelCase(message["item_name"])
    item_name_with_number = self.__getNameWithBrickNumber(item_name, tree_item_name)
    tree_name = self.memory["tree_name"]
    self.dataModel.addItemToTree(tree_name,
                                 tree_item_name,
                                 item_name_with_number)
    pass

  def __getNameWithBrickNumber(self, item_name, tree_item_name):
    if "_" in tree_item_name:
      no, _ = tree_item_name.split("_")
      item_name_ = "%s_" % no + item_name
    else:
      item_name_ = item_name
    return item_name_

  # def renameItem(self, message):
  #   # tree_item_name = message["item_name"] #self.memory["tree_item_name"]
  #   old_name = self.memory["name"]
  #   item_name = message["item_name"]
  #   # item_name_with_number = self.__getNameWithBrickNumber(item_name, tree_item_name)
  #   path_to_leave = message["path_to_leave"]
  #   tree_name = self.memory["tree_name"]
  #   self.dataModel.renameItemInTree(tree_name,
  #                                   tree_item_name,
  #                                   item_name_with_number,
  #                                   path_to_leave)
  #   pass

  def removeItem(self, message):
    # tree_item_name = self.memory["tree_item_name"]
    item_name = message["item_name"]
    parent_name = message["parent_name"]
    tree_name = self.memory["tree_name"]
    self.dataModel.removeItem("trees", tree_name, parent_name, item_name)
    pass

  def instantiatePrimitive(self, message):
    pass
    tree_name = self.memory["tree_name"]
    primitive_type = message["type"]
    value = message["value"]
    self.dataModel.modifyPrimitiveValue(tree_name, primitive_type, value)

    pass

  def addLink(self, message):
    # check for no name in the brick is already in the path

    link_position = self.memory["tree_item_name"]
    path = message["path"]
    brick_name = message["brick_name"]
    brick_names = self.dataModel.getAllNamesInABrickOrATree(brick_name, "brick")
    for name in brick_names:
      if name in path:
        makeMessageBox("the name %s is defined in the brick and the path -- link is not allowed" % name)
        return
    if link_position:
      if not brick_name:
        return

      tree_name = self.memory["tree_name"]
      self.dataModel.linkBrickToItem(tree_name,
                                     link_position,
                                     brick_name)

  def saveTrees(self, message):
    self.dataModel.saveBricksTreesAndInstances(self.project_name)
    self.frontEnd.markSaved()

  def extractInstance(self, message):
    tree_name = self.memory["tree_name"]
    self.dataModel.reduceGraph(tree_name)

  def putTreeList(self, message):
    tree_list = self.dataModel.getTreeList()
    self.frontEnd.putTreeList(tree_list)

  # def rememberTreeSelection(self, message):
  #   self.memory["tree_name"] = message["tree_name"]

  def showTree(self, message):
    if TIMING: start = time.time()
    try:
      tree_name = message["tree_name"]
    except:
      tree_name = self.memory["tree_name"]
    if TIMING: print("getting tuples", time.time() - start)
    instances = self.dataModel.instances

    paths, properties, leaves = self.dataModel.getTreePaths(tree_name)

    # graph, root = self.dataModel.getGraph(tree_name, "tree_name")
    # self.frontEnd.showNewTreeTree(graph, root, instances)
    self.frontEnd.showNewNewTreeTree(tree_name, paths, properties, leaves, instances)
    pass

    # ======================== trees

  def newTree(self, message):
    brick_name = message["brick_name"]
    tree_name = message["tree_name"]
    self.dataModel.newTree(tree_name, brick_name)

  def renameTree(self, message):
    old_name = self.memory["tree_name"]
    new_name = message["tree_name"]
    self.dataModel.renameTree(old_name, new_name)
    pass

  def deleteTree(self, message):
    tree_name = self.memory["tree_name"]
    self.dataModel.deleteTree(tree_name)

  def putBricksListForTree(self, message):
    brick_list = self.dataModel.getBrickList()
    self.frontEnd.putBricksListForTree(brick_list)

  def visualise(self, message):
    tree = self.memory["tree_name"]
    dataBrickTuples = self.dataModel.makeDataTuplesForGraph(tree,
                                                            "tree_name")
    class_names = [tree]  # sorted(self.dataModel.BRICK_GRAPHS.keys())
    graph = TreePlot(graph_name=tree, graph_triples=dataBrickTuples, class_names=class_names)
    graph.makeMe(tree)
    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, self.project_name) + "+%s_tree" % tree

    graph.dot.render(file_name_bricks, format="pdf")
    os.remove(file_name_bricks)

    path = file_name_bricks + ".pdf"
    if os.path.exists("/.dockerenv"):
      subprocess.Popen(['evince', str(path)])
      # subprocess.Popen(['okular', str(path)])
      # subprocess.Popen(['qpdfview --unique', str(path)])
      # makeMessageBox("cannot display pdf-file, open it locally", buttons=["OK"])
    elif sys.platform.startswith('linux'):
      subprocess.Popen(['xdg-open', str(path)])
    elif sys.platform.startswith('win32'):
      subprocess.Popen(['start', str(path)], shell=True)
    pass
