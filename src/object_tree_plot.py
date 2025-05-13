import graphviz


def plot_tree_graphviz(tree):
  # Create a new directed graph
  dot = graphviz.Digraph(comment='RDF Tree')
  dot.attr(rankdir='TB')  # Top to bottom direction

  def add_nodes(node, parent=None):
    # Get clean node name without namespace
    node_name = node.split('#')[-1] if '#' in str(node) else str(node)
    e_name = tree["nodes"][node]
    node_label = e_name.split('#')[-1] if '#' in str(e_name) else str(tree["nodes"][node])

    # Add node
    dot.node(node_name, label=node_label)

    # Add edge from parent if exists
    if parent:
      parent_name = str(parent)
      dot.edge(parent_name, node_name)

    # Recursively add children
    for child in tree["tree"][node]["children"]:
      add_nodes(child, node)

  # Start with root node's first child
  first_child = tree["tree"][0]["children"][0] if tree["tree"][0]["children"] else 0
  add_nodes(first_child)

  # Render the graph
  return dot


# Generate the visualization
# dot = plot_tree_graphviz(tree)
# dot.render(view=True)