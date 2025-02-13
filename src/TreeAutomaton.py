"""
automaton definition for PeriConto
"""
from graphviz import Digraph

from BricksAndTreeSemantics import RULES

UI_state = {
        "start"                                           : {
                "show"  : [
                        "exit",
                        "ontology_load",
                        ],
                "except": [],
                "action": [],
                },
        # note: ontology
        "load ontology"                                   : {
                "show"  : ["exit",
                           "tree_create",
                           "tree_list",
                           ],
                "except": [],
                "action": ["loadOntology",
                           "putBricksListForTree",
                           "putTreeList",
                           ],
                },
        # note: trees
        "new tree"                                        : {
                "show"  : ["exit",
                           # "tree_visualise",
                           # "ontology_save",
                           # "ontology_save_as",
                           "tree_create",
                           "tree_list",
                           ],
                "except": [],
                "action": ["newTree",
                           "putTreeList",
                           "markChanged",
                           ],
                },
        "selected tree"                                   : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_create",
                           "tree_rename",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [  # "newTree",
                        "rememberTreeSelection",
                        "getTreeDataTuples",
                        ],
                },
        "rename tree"                                   : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_create",
                           "tree_rename",
                           "tree_list",
                           ],
                "except": [],
                "action": [
                        "renameTree",
                        "putTreeList",
                           "markChanged",
                        ],
                },

        "%s in treeTree selected" % RULES["is_class"]     : {  # class in tree selected
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           "copy_tree",
                           ],
                "except": [],
                "action": [],
                },

        "%s in treeTree selected" % RULES["is_member"]    : { # member selected
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           "tree_link_existing_class"
                           ],
                "except": [],
                "action": [],
                },

        "%s in treeTree selected" % RULES["is_defined_by"]: { # linked member selected
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [],
                },

        "%s in treeTree selected" % RULES["value"]        : { # value selected
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [],
                },

        "%s in treeTree selected" % RULES["integer"]      : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [],
                },
        "%s in treeTree selected" % RULES["decimal"]      : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [],
                },
        "%s in treeTree selected" % RULES["uri"]          : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [],
                },
        "%s in treeTree selected" % RULES["boolean"]      : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": [],
                },
        "link" : {
                "show"  : ["exit",
                           "tree_visualise",
                           "ontology_save",
                           "ontology_save_as",
                           "tree_list",
                           "tree_tree",
                           ],
                "except": [],
                "action": ["addLink"],
                },
        "save"                                            : {
                "show"  : ["do_nothing"],
                "action": ["saveTrees"],
                },
        "save as"                                         : {
                "show"  : ["do_nothing"],
                "action": ["saveTreeWithNewName"],
                },
        "visualise"                                       : {
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
  file_name = "automaton"
  g.dot.render(file_name, format="pdf")
