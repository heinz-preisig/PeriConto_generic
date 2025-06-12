"""
from chatGpt : "RDF graph connectivity check" and "separate unconnected graphs
"""
import rdflib
import networkx as nx


def extract_subgraphs(rdf_file, output_format="turtle"):
  g = rdflib.Graph()
  g.parse(rdf_file, format="turtle")  # Adjust format if needed

  # Create a directed graph
  nx_graph = nx.DiGraph()

  # Add triples as edges
  for s, p, o in g:
    nx_graph.add_edge(s, o, predicate=p)

  # Get weakly connected components (for directed graphs)
  components = list(nx.weakly_connected_components(nx_graph))

  subgraphs = []
  for i, component in enumerate(components):
    subgraph = rdflib.Graph()
    for s, p, o in g:
      if s in component and o in component:
        subgraph.add((s, p, o))

    subgraphs.append(subgraph)
    # Save each subgraph separately
    subgraph.serialize(f"subgraph_{i}.{output_format}", format=output_format)

  return subgraphs


# Run the function
rdf_file = "example.rdf"  # Replace with your RDF file
subgraphs = extract_subgraphs(rdf_file)

print(f"Extracted {len(subgraphs)} separate subgraphs.")
