import os
import sys

# from PeriConto import debugging
# from PeriConto import debugging
from PeriContoDataModel import DataModel

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
    self.state = "start"
    self.previousEvent = "start"
    self.UI_state = {
            "start"          : {
                    "show": ["ontology_control",
                             "ontology_load",
                             "ontology_create"],
                    "hide": ["ontology_save",
                             "ontology_save_as",
                             "tab_lists_control",
                             "primitives_control",
                             ],
                    },
            "create ontology": {
                    "show": ["ontology_save",
                             "ontology_save_as",
                             "tab_lists_control",
                             "brick_control",
                             "brick_create"],
                    "hide": ["ontology_load",
                             "ontology_create",
                             "brick_delete",
                             "brick_add_item",
                             "brick_remove_item",
                             "brick_add_primitive",
                             "brick_remove_primitive",
                             "brick_rename",
                             "tree_control",
                             "Tree",
                             "tree_select_brick",
                             ],
                    },
            "load ontology"  : {
                    "show": ["ontology_save",
                             "ontology_save_as",
                             "tab_lists_control",
                             "brick_control",
                             "brick_create",
                             "brick_delete",
                             "brick_add_item",
                             "brick_remove_item",
                             "brick_add_primitive",
                             "brick_remove_primitive",
                             "brick_rename",
                             "tree_control",
                             "Tree",
                             "tree_select_brick"
                             ],
                    "hide": ["ontology_create",
                             "ontology_load",
                             ],
                    },
            "new brick"      : {
                    "show": ["ontology_save",
                             "ontology_save_as",
                             "tab_lists_control",
                             "brick_control",
                             "brick_create",
                             "brick_delete",
                             "brick_add_item",
                             "brick_remove_item",
                             "brick_add_primitive",
                             "brick_remove_primitive",
                             "brick_rename",
                             "tree_control",
                             "Tree",
                             "tree_select_brick"
                             ],
                    "hide": ["ontology_create",
                             "ontology_load",
                             ],
                    },
            "selected brick" : {
                    "show": ["ontology_save",
                             "ontology_save_as",
                             "tab_lists_control",
                             "brick_control",
                             "brick_create",
                             "brick_delete",
                             "brick_add_item",
                             "brick_remove_item",
                             "brick_add_primitive",
                             "brick_remove_primitive",
                             "brick_rename",
                             "tree_control",
                             "Tree",
                             "tree_select_brick"
                             ],
                    "hide": ["ontology_create",
                             "ontology_load",
                             ],
                    },
            }
    self.actions = {
            "start"          : [],
            "create ontology": ["createOntology",
                                "markChanged",
                                "putBrickList"],
            "load ontology"  : ["loadOntology",
                                # "getBrickDataTuples",
                                "putBrickList",
                                ],
            "new brick"      : ["newBrick",
                                "getBrickDataTuples",
                                "putBrickList",
                                "markChanged",
                                ],
            "selected brick"  : ["getBrickDataTuples",
                                 "putBrickDataTuples",
                                 ]
            }
    pass

    self.frontEnd = frontEnd

  def processEvent(self, message):
    event = message["event"]
    if not event:
      event = self.previousEvent
    ui_state = self.UI_state[event]
    self.frontEnd.setInterface(ui_state)
    for a in self.actions[event]:
      c = "self.%s(message)" % a
      r = exec(c)
      print(r)
    self.previousEvent = event

  def createOntology(self, message):
    debugging("> action", message)
    name = message["name"]
    self.dataModel = DataModel(name)
    self.currentGraphName = name
    pass

  def loadOntology(self, message):
    name = message["name"]
    self.dataModel = DataModel(None)
    self.dataModel.loadFromFile(name)
    self.currentGraphName = name
    pass

  def markChanged(self, message):
    self.frontEnd.markChanged()

  def getBrickDataTuples(self, message):
    name = message["name"]
    self.dataBrickTuples = self.dataModel.makeDataTuplesForGraph(name, "bricks")
    pass

  def putBrickList(self, message):
    brick_list = self.dataModel.getBrickList()
    self.frontEnd.showBrickList(brick_list)

  def newBrick(self, message):
    self.currentBrick = message["name"]
    self.dataModel.newBrick(self.currentBrick)

  def putBrickDataTuples(self, message):
    name = message["name"]
    tuples = self.dataBrickTuples
    self.frontEnd.showBrickTree(tuples, name)
