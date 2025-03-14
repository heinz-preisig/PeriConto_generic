import graphviz

# Create a new Digraph with Left-to-Right direction
dot = graphviz.Digraph()
dot.graph_attr["rankdir"] = "TD"  # Set graph direction Left to Right

# Add regular nodes
dot.node('A', 'Start')
dot.node('B', 'Process')
dot.node('C', 'End')

# Add edges
dot.edge('A', 'B', label='Step 1')
dot.edge('B', 'C', label='Step 2')

# Add a standalone annotation at the bottom
dot.node('note', 'This is an annotation', shape='plaintext')

# Force the annotation to be at the bottom
with dot.subgraph() as s:
    s.attr(rank='sink')  # Push to the bottom
    s.node('note')  # Ensure it is included

# Show the graph
dot.render(view=True)
