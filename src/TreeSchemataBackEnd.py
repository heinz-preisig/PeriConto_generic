import os
import sys

from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import RULES
from DataModel import DataModel
from TreeAutomaton import UI_state

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from graphviz import Digraph

DEBUGG = True


def debugging(*info):
  if DEBUGG:
    print("debugging", info)


# class AutomatonPlot()


class TreePlot:
  """
    Create Digraph plot
  """

  EDGE_COLOURS = {
          "is_class"     : "red",
          "is_member"    : "blue",
          "is_defined_by": "darkorange",
          "value"        : "black",
          "data_type"    : "green",
          # "comment"         : "green",
          # "integer"         : "darkorange",
          # "string"          : "cyan",
          "other"        : "orange",
          }

  NODE_SPECS = {
          "Class"    : {
                  "colour"   : "red",
                  "shape"    : "rectangle",
                  "fillcolor": "red",
                  "style"    : "filled",
                  },
          "member"   : {
                  "colour"   : "orange",
                  "shape"    : "",
                  "fillcolor": "white",
                  "style"    : "filled",
                  },
          "primitive": {
                  "colour"   : "blue",
                  "shape"    : "rectangle",
                  "fillcolor": "white",
                  "style"    : "filled",
                  },
          "ROOT"     : {
                  "colour"   : "red",
                  "shape"    : "rectangle",
                  "fillcolor": "white",
                  "style"    : "filled",
                  },
          "linked"   : {
                  "colour"   : "green",
                  "shape"    : "rectangle",
                  "fillcolor": "white",
                  "style"    : "filled",
                  },
          "other"    : {
                  "colour"   : None,
                  "shape"    : None,
                  "fillcolor": None,
                  "style"    : None,
                  },
          }
  NODE_SPECS["linked"] = NODE_SPECS["Class"]

  def __init__(self, graph_name, graph_triples, class_names):
    self.classes = class_names
    self.triples = graph_triples
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

  def addEdge(self, From, To, type, dir):
    try:
      colour = self.EDGE_COLOURS[type]
    except:
      colour = self.EDGE_COLOURS["other"]
    if dir == -1:
      self.dot.edge(From, To,
                    color=colour,
                    label=type
                    )
    elif dir == 1:
      self.dot.edge(To, From,
                    color=colour,
                    label=type
                    )
    else:
      print(">>>>>>>>>>>>>>>> should not come here")

  def makeMe(self, root):
    self.addNode(root, "Class")
    self.__makeGraph(origin=[root], stack=[])

  def __makeGraph(self, origin=[], stack=[]):
    for q in self.triples:
      if q not in stack:
        s, p, o, dir = q
        if s != origin:
          type = RULES[p]
          self.addNode(o, type)
          self.addEdge(s, o, p, dir)
          stack.append(q)  # (s, p, o))
          self.__makeGraph(origin=s, stack=stack)


class BackEnd():
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
    self.frontEnd.setRules(RULES)

  def processEvent(self, message):
    debugging(">>>> message ", message)
    event = message["event"]
    self.fail = False
    for a in self.UI_state[event]["action"]:
      if a == "loadOntology":
        self.loadOntology(message)
      elif a == "putBricksListForTree":
        self.putBricksListForTree(message)
      elif a == "putTreeList":
        self.putTreeList(message)
      elif a == "tree_create":
        self.createTree(message)
      elif a == "newTree":
        self.newTree(message)
      # elif a == "rememberTreeSelection":
      #   self.rememberTreeSelection(message)
      elif a == "renameTree":
        self.renameTree(message)
      elif a == "getTreeDataTuples":
        self.getTreeDataTuples(message)
      elif a == "saveTrees":
        self.saveTrees(message)
      elif a == "saveTreeWithNewName":
        self.saveTreeWithNewName(message)
      elif a == "visualise":
        self.visualise(message)
      elif a == "markChanged":
        self.markChanged(message)
      elif a == "addLink":
        self.addLink(message)
      elif a == "addItem":
        self.addItem(message)
      else:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> oops no such command", a)

    if len(self.UI_state[event]["show"]) > 0:
      if self.UI_state[event]["show"][0] == "do_nothing":
        return

    if (not event) or self.fail:
      event = self.previousEvent

    if not self.fail:
      ui_state = self.UI_state[event]
      self.frontEnd.setInterface(ui_state["show"])
      debugging("show what", ui_state["show"])
      self.previousEvent = event
    else:
      for a in self.UI_state[event]["except"]:
        c = "self.%s(message)" % a
        r = exec(c)
        debugging("execute:", c)

    self.memory.update(message)

  def loadOntology(self, message):
    name = message["project_name"]
    self.project_name = name
    self.dataModel = DataModel(name)
    self.dataModel.loadFromFile(name)
    pass

  def markChanged(self, message):
    self.frontEnd.markChanged()

  def saveTreeWithNewName(self, message):
    project_name = message["project_name"]
    file_name = self.dataModel.makeFileName(project_name,
                                            what="bricks")
    self.dataModel.saveBricks(file_name=file_name)
    file_name = self.dataModel.makeFileName(project_name,
                                            what="trees")
    self.dataModel.saveTrees(file_name=file_name)
    self.frontEnd.markSaved()
    self.project_name = project_name

  def createTree(self, message):
    tree_name = message["tree_name"]
    self.dataModel.newTree(tree_name)
    self.memory["tree_name"] = tree_name
    pass

  def addItem(self, message):
    item_name = message["item_name"]
    tree_item_name = self.memory["tree_item_name"]
    # self.dataModel.addItem(brick, ClassOrSubClass, name)
    pass

  def addLink(self, message):
    link_position = self.memory["tree_item_name"]
    if link_position:
      tree_item_name = self.memory["tree_item_name"]
      brick_name = message["brick_name"]
      tree_name = self.memory["tree_name"]
      self.dataModel.linkBrickToItem(tree_name,
                                     tree_item_name,
                                     brick_name)

  def saveTrees(self, message):
    self.dataModel.saveTrees()
    self.frontEnd.markSaved()

  def putTreeList(self, message):
    tree_list = self.dataModel.getTreeList()
    self.frontEnd.putTreeList(tree_list)

  def rememberTreeSelection(self, message):
    self.memory["tree_name"] = message["tree_name"]

  def getTreeDataTuples(self, message):
    tree_name = message["tree_name"]
    dataTreeTuples = self.dataModel.makeDataTuplesForGraph(tree_name, "tree_name")
    self.frontEnd.showTreeTree(dataTreeTuples, tree_name)
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

  def putBricksListForTree(self, message):
    brick_list = self.dataModel.getBrickList()
    self.frontEnd.putBricksListForTree(brick_list)

  def visualise(self, message):
    tree = self.memory["tree_name"]
    dataBrickTuples = self.dataModel.makeDataTuplesForGraph(tree,
                                                            "tree_name")
    class_names = sorted(self.dataModel.BRICK_GRAPHS.keys())
    graph = TreePlot(graph_name=tree, graph_triples=dataBrickTuples, class_names=class_names)
    graph.makeMe(tree)
    file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, self.project_name) + "+%s_tree" % tree

    graph.dot.render(file_name_bricks, format="pdf")
    os.remove(file_name_bricks)
    pass
