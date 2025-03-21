import os
import subprocess
import sys

from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import PRIMITIVES
from BricksAndTreeSemantics import RULES
from BricksAutomaton import UI_state
from DataModel import DataModel
from Utilities import TreePlot
from Utilities import camelCase
from Utilities import classCase
from Utilities import debugging

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])


# DEBUGG = False


class BackEnd():
  def __init__(self, frontEnd):
    self.memory = {
            "brick"            : None,
            "item"             : None,
            "tree schema"      : None,
            "tree instantiated": None,
            }

    self.state = "start"
    self.previousEvent = "start"

    self.UI_state = UI_state

    self.frontEnd = frontEnd
    self.rules = RULES
    self.frontEnd.setRules(RULES, PRIMITIVES)

  def processEvent(self, message):
    debugging(">>>> message ", message)
    event = message["event"]
    # self.fail = False
    for a in self.UI_state[event]["action"]:
      if a == "createOntology":
        self.createOntology(message)
      elif a == "putBrickList":
        self.putBrickList(message)
      elif a == "markChanged":
        self.markChanged(message)
      elif a == "loadOntology":
        self.loadOntology(message)
      elif a == "newBrick":
        self.newBrick(message)
      elif a == "selectedBrick":
        self.selectedBrick(message)
      elif a == "showBrickTree":
        self.showBrickTree(message)
      elif a == "removeBrick":
        self.removeBrick(message)
      elif a == "selectedClassInBrickTree":
        self.selectedClassInBrickTree(message)
      elif a == "selectedItemInBrickTree":
        self.selectedItemInBrickTree(message)
      elif a == "selectedValueInBrickTree":
        self.selectedValueInBrickTree(message)
      elif a == "changePrimitive":
        self.changePrimitive(message)
      elif a == "putAllNames":
        self.putAllNames(message)
      elif a == "renameItem":
        self.renameItem(message)
      elif a == "addItem":
        self.addItem(message)
      elif a == "addPrimitive":
        self.addPrimitive(message)
      elif a == "removeItemFromBrickTree":
        self.removeItemFromBrickTree(message)
      elif a == "saveBricks":
        self.saveBricks(message)
      elif a == "saveBricksWithNewName":
        self.saveBricksWithNewName(message)
      elif a == "visualise":
        self.visualise(message)
      else:
        print(">>>>>>>>>>> -- no such command: ", a)
        print("\n message was:", message)

    if len(self.UI_state[event]["show"]) > 0:
      if self.UI_state[event]["show"][0] == "do_nothing":
        return

    ui_state = self.UI_state[event]
    self.frontEnd.setInterface(ui_state["show"])
    self.previousEvent = event

    self.memory.update(message)

  def createOntology(self, message):
    debugging("> action", message)
    name = message["name"]
    self.project_name = name
    self.dataModel = DataModel(name)
    pass

  def loadOntology(self, message):
    name = message["name"]
    self.project_name = name
    self.dataModel = DataModel(name)
    self.dataModel.loadFromFile(name)
    pass

  def selectedBrick(self, message):
    self.memory["brick"] = message["name"]
    debugging("selected brick is ", message["name"])

  def markChanged(self, message):
    self.frontEnd.markChanged()

  def showBrickTree(self, message):
    brick_name = self.memory["brick"]
    self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(brick_name, "bricks")
    self.frontEnd.showBrickTree(self.dataBrickTuples, brick_name)

  def putBrickList(self, message):
    self.brick_list = self.dataModel.getBrickList()
    self.frontEnd.showBrickList(self.brick_list)

  def putAllNames(self, message):
    brick_name = self.memory["brick"]
    names = self.dataModel.getAllNamesInTheBrick(brick_name, "brick")
    self.frontEnd.setAllNames(names)

  def newBrick(self, message):
    name = message["name"]
    self.dataModel.newBrickOrTreeGraph("bricks", name)
    self.memory["brick"] = name

  def removeBrick(self, message):
    name = self.memory["name"]
    self.dataModel.removeBrick(name)

  def selectedClassInBrickTree(self, message):
    self.memory["item"] = message["name"]
    # type = message["type"]

  def selectedValueInBrickTree(self, message):
    self.memory["item"] = message["name"]

  def selectedItemInBrickTree(self, message):
    self.memory["item"] = message["name"]
    pass

  def addItem(self, message):
    ClassOrSubClass = self.memory["item"]
    brick_name = self.memory["brick"]
    name = message["name"]
    self.dataModel.addItem(brick_name, ClassOrSubClass, name)

  def addPrimitive(self, message):
    brick_name = self.memory["brick"]
    primitive = message["type"]
    ClassOrSubClass = self.memory["item"]
    name = message["name"]
    self.dataModel.addPrimitive(brick_name,
                                ClassOrSubClass,
                                name, primitive)

  def changePrimitive(self, message):
    debugging("-- changePrimitive")
    parent_name = self.memory["name"]
    brick_name = self.memory["brick"]
    new_type = message["type"]
    self.dataModel.modifyPrimitiveType(brick_name, parent_name, new_type)

  def renameBrick(self, message):
    old_name = self.memory["brick"]
    new_name = message["name"]
    if new_name:
      self.dataModel.renameBrick(old_name, classCase(new_name))

  def saveBricks(self, message):
    self.dataModel.saveBricks()
    self.frontEnd.markSaved()

  def saveBricksWithNewName(self, message):
    name = message["name"]
    file_name = self.dataModel.makeFileName(name, what="bricks")
    self.dataModel.saveBricks(file_name=file_name)
    self.frontEnd.markSaved()

  def renameItem(self, message):
    old_name = self.memory["brick"]
    item_name = self.memory["item"]
    item_names = self.dataModel.getAllNamesInTheBrick(old_name, "brick")
    newName = self.frontEnd.askForItemName("provide new name for item %s" % item_name, item_names)
    if newName:
      self.dataModel.renameItem(old_name, item_name, camelCase(newName))

      self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(old_name, "bricks")
      self.frontEnd.showBrickTree(self.dataBrickTuples, old_name)

  def removeItemFromBrickTree(self, message):
    name = self.memory["item"]
    brick = self.memory["brick"]
    self.dataModel.removeItem("bricks", brick, name)
    pass

  def visualise(self, message):
    tree = self.memory["brick"]
    dataBrickTuples = self.dataModel.makeDataTuplesForGraph(tree, "bricks")
    class_names = sorted(self.dataModel.BRICK_GRAPHS.keys())
    graph = TreePlot(graph_name=tree, graph_triples=dataBrickTuples, class_names=class_names)
    graph.makeMe(tree)
    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, self.project_name) + "+%s" % tree

    graph.dot.render(file_name_bricks, format="pdf")
    os.remove(file_name_bricks)

    path = file_name_bricks + ".pdf"
    if sys.platform.startswith('linux'):
      subprocess.Popen(['xdg-open', str(path)])
    elif sys.platform.startswith('win32'):
      subprocess.Popen(['start', str(path)], shell=True)
    del graph
    pass
