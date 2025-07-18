import os
import subprocess
import sys

from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import PRIMITIVES
from BricksAndTreeSemantics import RULES
from BricksAutomaton import UI_state
from DataModelNoBrickNumbers import DataModel
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
      # ontology
      if a == "OntologyCreate":
        self.OntologyCreate(message)
      elif a == "OntologyLoad":
        self.OntologyLoad(message)
      elif a == "OntologyChanged":
        self.OntologyChanged(message)
      elif a == "OntologySave":
        self.OntologySave(message)
      elif a == "OntologySaveWithNewName":
        self.OntologySaveWithNewName(message)
        # bricks
      elif a == "BrickListPut":
        self.BrickListPut(message)
      elif a == "BrickNew":
        self.BrickNew(message)
      elif a == "BrickSelected":
        self.BrickSelected(message)
      elif a == "BrickTreeShow":
        self.BrickTreeShow(message)
      elif a == "BrickRename":
        self.BrickRename(message)
      elif a == "BrickRemove":
        self.BrickRemove(message)
      elif a == "BrickClassSelected":
        self.BrickClassSelected(message)
      elif a == "BrickItemSelected":
        self.BrickItemSelected(message)
      elif a == "BrickValueSelected":
        self.BrickValueSelected(message)
      elif a == "BrickVisualise":
        self.BrickVisualise(message)
        # items
      elif a == "ItemAdd":
        self.ItemAdd(message)
      elif a == "ItemRemove":
        self.ItemRemove(message)
      elif a == "ItemRename":
        self.ItemRename(message)
      # primitives
      elif a == "PrimitiveAdd":
        self.PrimitiveAdd(message)
      elif a == "PrimitiveRemove":
        self.PrimitiveRemove(message)
      elif a == "PrimitiveRename":
        self.PrimitiveRename(message)
      elif a == "PrimitiveChange":
        self.PrimitiveChange(message)
      # tree
      elif a == "putAllNames":
        self.putAllNames(message)
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

  def OntologyCreate(self, message):
    debugging("> action", message)
    name = message["name"]
    self.project_name = name
    self.dataModel = DataModel(name)
    pass

  def OntologyLoad(self, message):
    name = message["name"]
    self.project_name = name
    self.dataModel = DataModel(name)
    self.dataModel.loadFromFile()
    pass

  def BrickSelected(self, message):
    self.memory["brick"] = message["name"]
    debugging("selected brick is ", message["name"])

  def OntologyChanged(self, message):
    self.frontEnd.OntologyChanged()

  def BrickTreeShow(self, message):
    brick_name = self.memory["brick"]
    self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(brick_name, "bricks")
    self.frontEnd.BrickTreeShow(self.dataBrickTuples, brick_name)

  def BrickListPut(self, message):
    self.brick_list = self.dataModel.getBrickList()
    self.frontEnd.showBrickList(self.brick_list)

  def putAllNames(self, message):
    brick_name = self.memory["brick"]
    names = self.dataModel.getAllNamesInABrickOrATree(brick_name, "brick")
    self.frontEnd.setAllNames(names)

  def BrickNew(self, message):
    name = message["name"]
    self.dataModel.newBrick(name)
    self.memory["brick"] = name

  def BrickRemove(self, message):
    name = self.memory["name"]
    self.dataModel.removeBrick(name)

  def BrickClassSelected(self, message):
    self.memory["item"] = message["name"]
    # type = message["type"]

  def BrickValueSelected(self, message):
    self.memory["item"] = message["name"]

  def BrickItemSelected(self, message):
    self.memory["item"] = message["name"]
    pass

  def ItemAdd(self, message):
    ClassOrSubClass = self.memory["item"]
    brick_name = self.memory["brick"]
    name = message["name"]
    self.dataModel.item_add(brick_name, ClassOrSubClass, name)

  def PrimitiveAdd(self, message):
    brick_name = self.memory["brick"]
    primitive = message["type"]
    ClassOrSubClass = self.memory["item"]
    name = message["name"]
    self.dataModel.primitive_add(brick_name,
                                 ClassOrSubClass,
                                 name, primitive)

  def PrimitiveChange(self, message):
    debugging("-- PrimitiveChange")
    parent_name = self.memory["name"]
    brick_name = self.memory["brick"]
    new_type = message["type"]
    self.dataModel.modifyPrimitiveType(brick_name, parent_name, new_type)

  def BrickRename(self, message):
    old_name = self.memory["brick"]
    new_name = message["name"]
    if new_name:
      self.dataModel.renameBrick(old_name, classCase(new_name))
      self.memory["brick"] = new_name

  def OntologySave(self, message):
    self.dataModel.saveBricks(self.project_name)
    self.frontEnd.markSaved()

  def OntologySaveWithNewName(self, message):
    name = message["name"]
    self.dataModel.saveBricks(name)
    self.frontEnd.markSaved()

  def ItemRename(self, message):
    old_name = message["name"]
    current_brick = self.memory["brick"]
    type = message["type"]
    item_names = self.dataModel.getAllNamesInABrickOrATree(current_brick, "brick")
    newName = self.frontEnd.askForItemName("provide new name for item %s" % old_name, item_names)
    if newName:
      new_name = camelCase(newName)
      self.dataModel.renameItemInBrick(current_brick, old_name, type, new_name)


  def PrimitiveRename(self, message):
    old_name = message["name"]
    parent_name = message["parent_name"]
    current_brick = self.memory["brick"]
    type = message["type"]
    item_names = self.dataModel.getAllNamesInABrickOrATree(current_brick, "brick")
    newName = self.frontEnd.askForItemName("provide new name for item %s" % old_name, item_names)
    if newName:
      new_name = newName.title().replace(" ", "") #camelCase(newName)
      self.dataModel.renameItemInBrick(current_brick, old_name, parent_name, new_name)
      self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(current_brick, "bricks")
      self.frontEnd.BrickTreeShow(self.dataBrickTuples, current_brick)

  def PrimitiveRemove(self, message):
    self.ItemRemove(message)

  def ItemRemove(self, message):
    item_name = message["name"]
    parent_name = message["parent_name"]
    current_brick = self.memory["brick"]
    self.dataModel.removeItem("bricks", current_brick, parent_name, item_name)
    pass

  def BrickVisualise(self, message):
    tree = self.memory["brick"]
    dataBrickTuples = self.dataModel.makeDataTuplesForGraph(tree, "bricks")
    class_names = sorted(self.dataModel.BRICK_GRAPHS.keys())
    graph = TreePlot(graph_name=tree, graph_triples=dataBrickTuples, class_names=class_names)
    graph.makeMe(tree)
    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, self.project_name) + "+%s" % tree

    graph.dot.render(file_name_bricks, format="pdf")
    os.remove(file_name_bricks)

    path = file_name_bricks + ".pdf"
    if os.path.exists("/.dockerenv"):
      subprocess.Popen(['evince', str(path)])
    elif sys.platform.startswith('linux'):
      subprocess.Popen(['xdg-open', str(path)])
    elif sys.platform.startswith('win32'):
      subprocess.Popen(['start', str(path)], shell=True)
    del graph
    pass
