"""
automaton definition for BrickSchema
"""
from graphviz import Digraph

UI_state = {
        "start"                         : {
                "show"  : [
                        "exit",
                        "ontology_create",
                        "ontology_load",
                        ],
                "except": [],
                "action": [],
                },
        # note: ontology
        "create ontology"               : {
                "show"  : ["exit",
                           "ontology_save",
                           "ontology_save_as",
                           # "tabs",
                           "brick_create",
                           ],
                "except": [],
                "action": ["createOntology",
                           "putBrickList",
                           "markChanged", ],
                },
        "load ontology"                 : {
                "show"  : ["exit",
                           # "tabs",
                           "brick_create",
                           "brick_list",
                           "ontology_create",
                           # "tree_create",
                           # "tree_list",
                           ],
                "except": [],
                "action": ["loadOntology",
                           "putBrickList",
                           ],
                },
        # note: bricks
        "new brick"                     : {
                "show"  : ["exit",
                           "ontology_save",
                           "ontology_save_as",
                           # "tabs",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           ],
                "except": [],
                "action": ["newBrick",
                           "putBrickList",
                           "markChanged",
                           ],
                },
        "selected brick"                : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           # "tabs",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           "brick_tree",
                           ],
                "except": [],
                "action": ["selectedBrick",
                           "showBrickTree",
                           "putAllNames",
                           ],
                },
        "rename brick"                  : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           # "tabs",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           ],
                "except": [],
                "action": ["renameBrick",
                           "putBrickList",
                           "putAllNames",
                           "markChanged", ],
                },
        "remove brick"                  : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           # "tabs",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           ],
                "except": [],
                "action": ["removeBrick",
                           "putBrickList",
                           "putAllNames",
                           "markChanged", ],
                },
        # note: selection in brick tree
        "Class in brick tree selected"  : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_create",
                           "brick_tree",
                           "brick_add_item",
                           "brick_add_primitive",
                           ],
                "except": [],
                "action": ["selectedClassInBrickTree"],
                },
        "Item in brick tree selected"   : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           "brick_tree",
                           "brick_add_item",
                           "brick_add_primitive",
                           "brick_remove_item",
                           "brick_item_or_primitive_rename",
                           ],
                "except": [],
                "action": ["selectedItemInBrickTree"],
                },
        "Value in brick tree selected"  : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           "brick_remove_item",
                           "brick_item_or_primitive_rename",
                           "brick_change_primitive",
                           ],
                "except": [],
                "action": ["selectedValueInBrickTree",
                           ],
                },
        "string in brick tree selected" : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": [],
                },
        "integer in brick tree selected": {
                "show"  : [
                        "exit",
                        "ontology_save",
                        "ontology_save_as",
                        "brick_list",
                        "brick_tree",
                        ],
                "except": [],
                "action": [],
                },
        "decimal in brick tree selected": {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": [],
                },
        "uri in brick tree selected"    : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": [],
                },
        "boolean in brick tree selected": {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": [],
                },
        "add item"       : {
                "show": ["exit",
                         "tree_visualise",
                         "ontology_save",
                         "ontology_save_as",
                         "brick_list",
                         "brick_tree",
                         ], "except": [],
                "action": ["addItem",
                           "putBrickList",
                           "showBrickTree",
                           "putAllNames",
                           "markChanged", ],
                },
        "add primitive"    : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": ["addPrimitive",
                           "showBrickTree",
                           "putAllNames",
                           "markChanged", ],
                },
        "change primitive"    : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": ["changePrimitive",
                           "showBrickTree",
                           "putAllNames",
                           "markChanged", ],
                },
        "Value rename"                  : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           "brick_tree",
                           ],
                "except": [],
                "action": ["renameItem",
                           "markChanged",
                           "showBrickTree",
                           "putAllNames",
                           ],
                },
        "Item rename"                   : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_create",
                           "brick_remove",
                           "brick_rename",
                           "brick_tree",
                           ],
                "except": [],
                "action": ["renameItem",
                           "putAllNames",
                           "markChanged",
                           "showBrickTree",
                           ],
                },
        "remove item from brick tree"   : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "brick_list",
                           "brick_tree",
                           ],
                "except": [],
                "action": ["removeItemFromBrickTree",
                           "markChanged",
                           "showBrickTree",
                           "putAllNames",
                           ],
                },
        # note: tab changes
        "save"                          : {
                "show"  : ["do_nothing"],
                "action": ["saveBricks"],
                },
        "save as"                       : {
                "show"  : ["do_nothing"],
                "action": ["saveBricksWithNewName"],
                },
        "visualise"                     : {
                "show"  : ["do_nothing"],
                "action": ["visualise"],
                },
        }

NODE_SPECS = {
        "event" : {
                "colour"   : "red",
                "shape"    : "rectangle",
                "fillcolor": "red",
                "style"    : "filled",
                },
        "show"  : {
                "colour"   : "orange",
                "shape"    : "",
                "fillcolor": "white",
                "style"    : "filled",
                },
        "action": {
                "colour"   : "blue",
                "shape"    : "rectangle",
                "fillcolor": "white",
                "style"    : "filled",
                },
        }
EDGE_COLOURS = {
        "event" : "red",
        "show"  : "blue",
        "action": "darkorange",
        }


class AutomatonPlot:

  def __init__(self):
    self.dot = Digraph("PeriConto automaton")
    self.dot.graph_attr["rankdir"] = "LR"

  def makeAutomatonPlot(self):

    for n in sorted(UI_state):
      dot = self.dot
      specs = NODE_SPECS["event"]
      dot.node(n,
               color=specs["colour"],
               shape=specs["shape"],
               fillcolor=specs["fillcolor"],
               style=specs["style"],
               )
      show_node = "%s show" % n
      dot.node(show_node, style="filled", fillcolor="orange")
      dot.edge(n, show_node,
               color="green")
      dot.edge(n, show_node,
               color="red",
               )
      for s in UI_state[n]["show"]:
        dot.node(s,
                 color=specs["colour"],
                 shape=specs["shape"],
                 fillcolor=specs["fillcolor"],
                 style=specs["style"],
                 )
        dot.edge(show_node, s,
                 color="black")

      action_node = "%s action" % n
      dot.node(action_node, style="filled", fillcolor="green")
      dot.edge(n, action_node)
      for a in UI_state[n]["action"]:
        dot.node(a,
                 color=specs["colour"],
                 shape=specs["shape"],
                 fillcolor=specs["fillcolor"],
                 style=specs["style"],
                 )
        dot.edge(action_node, a,
                 color="blue")


if __name__ == "__main__":
  g = AutomatonPlot()
  g.makeAutomatonPlot()
  file_name = "brick_automaton"
  g.dot.render(file_name, format="pdf")
