import os
import sys

from PeriContoAutomaton import UI_state
from PeriContoDataModel import DataModel
from PeriContoSemantics import PRIMITIVES

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from graphviz import Digraph

DEBUGG = True

def debugging(*info):
  if DEBUGG:
    print("debugging", info)


class TreePlot:
  """
    Create Digraph plot
  """

  EDGE_COLOURS = {
    "is_class": "red",
    "is_member": "blue",
    "is_defined_by": "darkorange",
    "value": "black",
    "data_type": "green",
    # "comment"         : "green",
    # "integer"         : "darkorange",
    # "string"          : "cyan",
    "other": "orange",
  }

  NODE_SPECS = {
    "Class": {
      "colour": "red",
      "shape": "rectangle",
      "fillcolor": "red",
      "style": "filled",
    },
    "member": {
      "colour": "orange",
      "shape": "",
      "fillcolor": "white",
      "style": "filled",
    },
    "primitive": {
      "colour": "blue",
      "shape": "rectangle",
      "fillcolor": "white",
      "style": "filled",
    },
    "ROOT": {
      "colour": "red",
      "shape": "rectangle",
      "fillcolor": "white",
      "style": "filled",
    },
    "linked": {
      "colour": "green",
      "shape": "rectangle",
      "fillcolor": "white",
      "style": "filled",
    },
    "other": {
      "colour": None,
      "shape": None,
      "fillcolor": None,
      "style": None,
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


class BackEnd():
  def __init__(self, frontEnd):
    self.memory = {
      "brick": None,
      "item in brick tree": None,
      "tree schema": None,
      "tree instantiated": None,
    }

    self.state = "start"
    self.previousEvent = "start"

    self.UI_state = UI_state

    self.frontEnd = frontEnd
    self.frontEnd.setPrimitives(PRIMITIVES)

  def processEvent(self, message):
    event = message["event"]
    if not event:
      event = self.previousEvent
    ui_state = self.UI_state[event]
    self.frontEnd.setInterface(ui_state["show"], ui_state["hide"])
    for a in self.UI_state[event]["action"]:  # self.actions[event]:
      c = "self.%s(message)" % a
      r = exec(c)
      print(r)
    self.previousEvent = event

  def createOntology(self, message):
    debugging("> action", message)
    name = message["name"]
    self.dataModel = DataModel(name)
    pass

  def loadOntology(self, message):
    name = message["name"]
    self.dataModel = DataModel(None)
    self.dataModel.loadFromFile(name)
    pass

  def markChanged(self, message):
    self.frontEnd.markChanged()

  def getBrickDataTuples(self, message):
    name = message["name"]
    self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(name, "bricks")
    self.memory["brick"] = name
    pass

  def putBrickList(self, message):
    self.brick_list = self.dataModel.getBrickList()
    self.frontEnd.showBrickList(self.brick_list)

  def newBrick(self, message):
    name = message["name"]
    self.dataModel.newBrick(name)
    self.memory["brick"] = name

  def putBrickDataTuples(self, message):
    name = message["name"]
    tuples = self.dataBrickTuples
    self.frontEnd.showBrickTree(tuples, name)

  def selectedItemInBrickTree(self, message): # todo: interface reset?
    name = message["name"]
    self.memory["item in brick tree"] = name
    type = message["type"]
    if type in PRIMITIVES:
      event = "primitive in brick tree selected"
      ui_state = self.UI_state[event]
      self.frontEnd.setInterface(ui_state["show"], ui_state["hide"])
    if type == "value":
      event = "value in brick tree selected"
      ui_state = self.UI_state[event]
      self.frontEnd.setInterface(ui_state["show"], ui_state["hide"])
    if name in self.brick_list:
      event = "brick root in brick tree selected"
      ui_state = self.UI_state[event]
      self.frontEnd.setInterface(ui_state["show"], ui_state["hide"])

    pass

  def getExistingItemNames(self, message):
    brick = self.memory["brick"]
    existing_names = self.dataModel.getAllNamesInTheBrick(brick, what="brick")
    name = self.frontEnd.askForItemName(existing_names)
    if name:
      ClassOrSubClass = self.memory["item in brick tree"]
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

  # def getExistingPrimitiveNames(self, message):
  #   brick = self.memory["brick"]
  #   existing_names = self.dataModel.getAllNamesInTheBrick(brick, what="brick")
  #   name = self.frontEnd.askForItemName(existing_names)
  #   if name:
  #     primitive = self.frontEnd.askForPrimitiveType(PRIMITIVES)
  #     ClassOrSubClass = self.memory["item in brick tree"]
  #     self.dataModel.addItem(brick, ClassOrSubClass, name)
  #     self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(brick, "bricks")
  #     self.frontEnd.showBrickTree(self.dataBrickTuples, brick)
  #   else:
  #     pass


  def removeItemFromBrickTree(self, message):
    name = self.memory["item in brick tree"]
    brick = self.memory["brick"]
    self.dataModel.removeItem(brick, name)
    message["name"] = brick
    pass
