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
from Utilities import debugging

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

DEBUGG = True


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
    self.frontEnd.setRules(RULES)

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
      elif a == "getBrickDataTuples":
        self.getBrickDataTuples(message)
      elif a == "putBrickDataTuples":
        self.putBrickDataTuples(message)
      elif a == "renameBrick":
        self.renameBrick(message)
      elif a == "removeBrick":
        self.removeBrick(message)
      elif a == "selectedClassInBrickTree":
        self.selectedClassInBrickTree(message)
      elif a == "selectedItemInBrickTree":
        self.selectedItemInBrickTree(message)
      elif a == "selectedValueInBrickTree":
        self.selectedValueInBrickTree(message)
      elif a == "getExistingItemNames":
        self.getExistingItemNames(message)
      elif a == "renameItem":
        self.renameItem(message)
      elif a == "removeItemFromBrickTree":
        self.removeItemFromBrickTree(message)
      elif a == "saveBricks":
        self.saveBricks(message)
      elif a == "saveBricksWithNewName":
        self.saveBricksWithNewName(message)
      elif a == "visualise":
        self.visualise(message)
      else:
        print("oooops -- no such command: ",a)

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
    print("selected brick is ", message["name"])

  def markChanged(self, message):
    self.frontEnd.markChanged()

  def getBrickDataTuples(self, message):
    name = self.memory["brick"]
    self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(name, "bricks")
    pass

  def putBrickList(self, message):
    self.brick_list = self.dataModel.getBrickList()
    self.frontEnd.showBrickList(self.brick_list)

  def newBrick(self, message):
    name = message["name"]
    self.dataModel.newBrickOrTreeGraph("bricks", name)
    self.memory["brick"] = name

  def removeBrick(self, message):
    name = self.memory["name"]
    self.dataModel.removeBrick(name)

  def putBrickDataTuples(self, message):
    name = self.memory["brick"]  # message["name"]
    tuples = self.dataBrickTuples
    self.frontEnd.showBrickTree(tuples, name)

  def selectedClassInBrickTree(self, message):
    self.memory["item"] = message["name"]
    # type = message["type"]

  def selectedValueInBrickTree(self, message):
    self.memory["item"] = message["name"]

  def selectedItemInBrickTree(self, message):
    self.memory["item"] = message["name"]
    pass

  def getExistingItemNames(self, message):
    brick = self.memory["brick"]
    existing_names = self.dataModel.getAllNamesInTheBrick(brick, what="brick")
    name_ = self.frontEnd.askForItemName("provide new item name", existing_names)
    if not name_:
      return
    name = camelCase(name_) # str(name_).title().replace(" ","")  # rule items are lower case
    if name:
      ClassOrSubClass = self.memory["item"]
      if message["event"] == "ask for adding a primitive":
        primitive = self.frontEnd.askForPrimitiveType(PRIMITIVES)
        if primitive:
          self.dataModel.addPrimitive(brick, ClassOrSubClass, name, primitive)
        else:
          return
      if message["event"] == "asks for adding an item":
        self.dataModel.addItem(brick, ClassOrSubClass, name)
      self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(brick, "bricks")
      self.frontEnd.showBrickTree(self.dataBrickTuples, brick)
    else:
      pass

  def renameBrick(self, message):
    brick = self.memory["brick"]
    brick_names = self.dataModel.getBrickList()
    newName = self.frontEnd.askForItemName("provide new name for brick %s" % brick, brick_names)
    if newName:
      self.dataModel.renameBrick(brick, classCase(newName)) #.upper())  #RULE: brick names are in capitals
      bricks = self.dataModel.getBrickList()
      self.frontEnd.showBrickList(bricks)

  def saveBricks(self, message):
    self.dataModel.saveBricks()
    self.frontEnd.markSaved()

  def saveBricksWithNewName(self, message):
    name = message["name"]
    file_name = self.dataModel.makeFileName(name, what="bricks")
    self.dataModel.saveBricks(file_name=file_name)
    self.frontEnd.markSaved()

  def renameItem(self, message):
    brick = self.memory["brick"]
    item_name = self.memory["item"]
    item_names = self.dataModel.getAllNamesInTheBrick(brick, "brick")
    newName = self.frontEnd.askForItemName("provide new name for item %s" % item_name, item_names)
    if newName:
      self.dataModel.renameItem(brick, item_name, camelCase(newName)) #newName.title().replace(" ",""))

      self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(brick, "bricks")
      self.frontEnd.showBrickTree(self.dataBrickTuples, brick)

  def removeItemFromBrickTree(self, message):
    name = self.memory["item"]
    brick = self.memory["brick"]
    self.dataModel.removeItem("bricks",brick, name)
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
