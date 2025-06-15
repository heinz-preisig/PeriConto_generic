import os
import sys
import unittest
from rdflib import Graph, Namespace, URIRef, XSD
from rdflib.namespace import RDF, RDFS

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from DataModelNoBrickNumbers import DataModel
from treeid import ObjectTree


class RDFToObjectTreeMapper:
  """Maps an RDF graph to an ObjectTree."""

  # Define XSD primitives that should be treated as leaves
  XSD_PRIMITIVES = {
          XSD.boolean,
          XSD.anyURI,
          XSD.decimal,
          XSD.integer,
          XSD.string,
          XSD.dateTime,
          XSD.date,
          XSD.time
          }

  def __init__(self, graph, root_name=None):
    """Initialize the mapper with an RDF graph and optional root name.

    Args:
        graph: An RDFLib Graph object
        root_name: Optional name of the root node. If not provided, will try to find it.
    """
    self.graph = graph
    self.root_name = root_name
    self.RDFS = RDFS
    self.RDF = RDF
    self.XSD = XSD
    self.A = Namespace("http://example.org/A#")
    self.visited = set()  # Track visited nodes to prevent cycles

  def map_to_object_tree(self):
    """Convert the RDF graph to an ObjectTree."""
    # Find the root node if not provided
    if self.root_name is None:
      # Look for a node that is an rdfs:Class
      for s, p, o in self.graph.triples((None, RDF.type, RDFS.Class)):
        self.root_name = self._get_name_from_uri(s)
        root_uri = s
        break
      else:
        raise ValueError("Could not find root node (rdfs:Class) in the graph")
    else:
      # Find the URI for the provided root name
      root_uri = None
      for s in self.graph.subjects(None, None):
        if self._get_name_from_uri(s) == self.root_name:
          root_uri = s
          break
      if root_uri is None:
        raise ValueError(f"Could not find node with name '{self.root_name}' in the graph")

    # Create the tree with the root node
    tree = ObjectTree(self.root_name)

    # Build the tree structure starting from the root
    # We pass None as parent since the root is already added
    self._build_tree_recursive(tree, root_uri, None)

    return tree

  def _ensure_node_exists(self, tree, node_name):
    """Ensure a node exists in the tree, creating it as a root if needed."""
    if node_name not in tree["IDs"]:
      # If the node doesn't exist, add it as a root
      # Get the root node ID to use as parent
      root_id = tree["IDs"][tree["nodes"][0]]  # Get the ID of the root node
      # Add the new node as a child of the root
      new_id = tree["tree"].addChild(root_id)
      # Update the mappings
      tree["nodes"][new_id] = node_name
      tree["IDs"][node_name] = new_id

  def _add_child_relationship(self, tree, child, parent):
    """Safely add a child relationship between two nodes."""
    # Ensure both nodes exist
    self._ensure_node_exists(tree, child)
    self._ensure_node_exists(tree, parent)

    # Add the child relationship if it doesn't already exist
    if child not in tree["IDs"] or parent not in tree["IDs"]:
      return

    # Use the ObjectTree's addChildtoNode method to add the relationship
    try:
      tree.addChildtoNode(child, parent)
    except Exception as e:
      print(f"Error adding child {child} to parent {parent}: {e}")

  def _is_primitive(self, node):
    """Check if a node is an XSD primitive type."""
    # Check if the node is directly an XSD type
    if isinstance(node, URIRef) and str(node).startswith(str(XSD)):
      return True

    # Check if the node has an rdf:type that's an XSD type
    for _, _, type_uri in self.graph.triples((node, RDF.type, None)):
      if str(type_uri).startswith(str(XSD)):
        return True

    return False

  def _get_primitive_value(self, node):
    """Get the value of a primitive node."""
    # For nodes with rdf:value, return that
    for _, _, value in self.graph.triples((node, RDF.value, None)):
      return str(value)
    return str(node)

  def _build_tree_recursive(self, tree, node, parent=None, visited=None):
    """Recursively build the tree structure.

    Args:
        node: The current node to process
        tree: The ObjectTree being built
        parent: The parent node, or None if this is the root
        visited: Set of already visited nodes to prevent cycles
    """
    if visited is None:
      visited = set()

    # Get the local name of the node (e.g., 'A' from 'http://example.org/A#A')
    node_name = self._get_name_from_uri(node)

    # Skip if we've already processed this node to prevent cycles
    if node_name in visited:
      return

    # Mark this node as visited
    visited.add(node_name)

    # Check if this is a primitive node
    if self._is_primitive(node):
      # For primitive nodes, just add them as leaves
      if parent is not None and node_name not in tree["IDs"]:
        self._add_child_relationship(tree, node_name, parent)
      return

    # Add the node to the tree if it's not already there
    if node_name not in tree["IDs"]:
      if parent is not None:
        self._add_child_relationship(tree, node_name, parent)
      else:
        # If no parent and not in tree, add as child of root
        root_name = tree["nodes"][0]  # Get the name of the root node
        if node_name != root_name:  # Don't add root as its own child
          self._add_child_relationship(tree, node_name, root_name)

    # Process rdfs:member relationships (subject is parent, object is child)
    for s, p, o in self.graph.triples((node, RDFS.member, None)):
      if isinstance(o, URIRef):
        child_name = self._get_name_from_uri(o)
        # Add the child relationship
        self._add_child_relationship(tree, child_name, node_name)
        # Recursively process the child
        self._build_tree_recursive(tree, o, node_name, visited.copy())

    # Process rdf:value relationships (subject is property, object is value)
    for s, p, o in self.graph.triples((node, RDF.value, None)):
      if isinstance(o, URIRef):
        value_name = self._get_name_from_uri(o)
        # Add the value as a child of this node
        self._add_child_relationship(tree, value_name, node_name)
        # Recursively process the value
        self._build_tree_recursive(tree, o, node_name, visited.copy())

    # Process properties (xsd:boolean, xsd:decimal, etc.)
    for s, p, o in self.graph.triples((node, None, None)):
      # Skip RDF/RDFS vocab
      if str(p).startswith(str(RDF)) or str(p).startswith(str(RDFS)):
        continue

      if isinstance(o, URIRef):
        prop_name = f"{self._get_name_from_uri(p)}_{self._get_name_from_uri(o)}"
        # Add the property as a child of this node
        self._add_child_relationship(tree, prop_name, node_name)
        # Recursively process the value
        self._build_tree_recursive(tree, o, prop_name, visited.copy())

    # Process inverse relationships (where this node is the object)
    for s, p, o in self.graph.triples((None, RDFS.member, node)):
      if isinstance(s, URIRef):
        parent_name = self._get_name_from_uri(s)
        # Add the parent relationship
        self._add_child_relationship(tree, node_name, parent_name)
        # Recursively process the parent
        self._build_tree_recursive(tree, s, None, visited.copy())

  def _get_name_from_uri(self, uri):
    """Extract the local name from a URI."""
    if '#' in str(uri):
      return str(uri).split('#')[-1]
    return str(uri).split('/')[-1]


class TestRDFToObjectTreeMapping(unittest.TestCase):
  """Test cases for mapping RDF trees to ObjectTrees."""

  def setUp(self):
    """Set up test fixtures."""
    self.test_file = os.path.join(os.path.dirname(__file__), 'TEST-TREE+bricks.trig')

  def test_load_rdf_tree(self):
    """Test loading an RDF tree from a file."""
    # Load the test RDF file
    g = Graph()
    g.parse(self.test_file, format="trig")

    # Define the expected namespace
    A = Namespace("http://example.org/A#")

    # Print all triples for debugging
    print("\nAll triples in the graph:")
    for s, p, o in g.triples((None, None, None)):
      # print(f"{s} {p} {o}")
      print(s, p, o)

    # Verify some expected triples are present
    self.assertTrue((A.A, RDF.type, RDFS.Class) in g, "A should be a class")
    self.assertTrue((A.Aa, RDFS.member, A.A) in g, "Aa should have A as member")
    self.assertTrue((A.Ab, RDFS.member, A.A) in g, "Ab should have A as member")
    self.assertTrue((A.Sa, RDF.value, A.Aa) in g, "Sa should have Aa as value")
    self.assertTrue((A.Sb, RDF.value, A.Ab) in g, "Sb should have Ab as value")

  def _verify_tree_structure(self, tree_structure):
    """Helper method to verify the tree structure."""
    # Print the tree structure for debugging
    print("\nTree structure:")
    for node, data in tree_structure.items():
      print(f"{node}: {data}")

    # Check that all expected nodes exist
    self.assertIn('A', tree_structure, "Node 'A' should exist")
    self.assertIn('Aa', tree_structure, "Node 'Aa' should exist")
    self.assertIn('Ab', tree_structure, "Node 'Ab' should exist")
    self.assertIn('Sa', tree_structure, "Node 'Sa' should exist")
    self.assertIn('Sb', tree_structure, "Node 'Sb' should exist")

    # The actual structure is:
    # A (root)
    # ├── Aa
    # │   └── Sa (boolean)
    # └── Ab
    #     └── Sb (boolean)

    # Check that A is the root (no ancestors)
    self.assertEqual(tree_structure['A']['ancestors'], [], "'A' should be the root with no ancestors")

    # Check that Aa and Ab are children of A
    self.assertIn('Aa', tree_structure['A']['children'], "'Aa' should be a child of 'A'")
    self.assertIn('Ab', tree_structure['A']['children'], "'Ab' should be a child of 'A'")

    # Check that Sa is a child of Aa and Sb is a child of Ab
    self.assertIn('Sa', tree_structure['Aa']['children'], "'Sa' should be a child of 'Aa'")
    self.assertIn('Sb', tree_structure['Ab']['children'], "'Sb' should be a child of 'Ab'")

    # Check that Sa and Sb are leaves (no children)
    self.assertEqual(tree_structure['Sa']['children'], [], "'Sa' should be a leaf node")
    self.assertEqual(tree_structure['Sb']['children'], [], "'Sb' should be a leaf node")

    # Check ancestor relationships
    self.assertEqual(tree_structure['Aa']['ancestors'], ['A'], "'Aa' should have 'A' as ancestor")
    self.assertEqual(tree_structure['Ab']['ancestors'], ['A'], "'Ab' should have 'A' as ancestor")

    # Check that Sa has both A and Aa as ancestors, regardless of order
    self.assertIn('A', tree_structure['Sa']['ancestors'], "'Sa' should have 'A' as ancestor")
    self.assertIn('Aa', tree_structure['Sa']['ancestors'], "'Sa' should have 'Aa' as ancestor")
    self.assertEqual(len(tree_structure['Sa']['ancestors']), 2, "'Sa' should have exactly 2 ancestors")

    # Check that Sb has both A and Ab as ancestors, regardless of order
    self.assertIn('A', tree_structure['Sb']['ancestors'], "'Sb' should have 'A' as ancestor")
    self.assertIn('Ab', tree_structure['Sb']['ancestors'], "'Sb' should have 'Ab' as ancestor")
    self.assertEqual(len(tree_structure['Sb']['ancestors']), 2, "'Sb' should have exactly 2 ancestors")

  def test_map_to_object_tree(self):
    """Test mapping an RDF tree to an ObjectTree with explicit root name."""
    # Load the test RDF file
    g = Graph()
    g.parse(self.test_file, format="trig")

    # Test with explicit root name 'A'
    mapper = RDFToObjectTreeMapper(g, root_name="A")
    object_tree = mapper.map_to_object_tree()

    # Verify the tree structure
    self.assertIsNotNone(object_tree, "Object tree should not be None")

    # Get the tree structure as a dictionary and verify it
    tree_structure = object_tree.makeTaggedTree()
    self._verify_tree_structure(tree_structure)

  def test_map_to_object_tree_auto_detect_root(self):
    """Test mapping an RDF tree to an ObjectTree with auto-detected root."""
    # Load the test RDF file
    g = Graph()
    g.parse(self.test_file, format="trig")

    # Test with auto-detection of root (should find 'A' as it's an rdfs:Class)
    mapper = RDFToObjectTreeMapper(g)  # No root_name provided
    object_tree = mapper.map_to_object_tree()

    # Verify the tree structure
    self.assertIsNotNone(object_tree, "Object tree should not be None")

    # Get the tree structure as a dictionary and verify it
    tree_structure = object_tree.makeTaggedTree()
    self._verify_tree_structure(tree_structure)

    # Print the tree structure for debugging
    print("\nTree structure:")
    for node, data in tree_structure.items():
      print(f"{node}: {data}")

  def test_map_tree2_to_object_tree(self):
    """Test mapping the test-tree2+bricks.ttl file to an ObjectTree."""
    # Load the RDF file
    rdf_file = os.path.join(os.path.dirname(__file__), "test-tree2+bricks.ttl")

    # Parse the RDF file into a graph
    g = Graph()
    g.parse(rdf_file, format="turtle")

    # Print all triples for debugging
    print("\nAll triples in the test-tree2+bricks.ttl graph:")
    for s, p, o in g:
      print(f"{s} {p} {o}")

    # Create the mapper with the graph
    mapper = RDFToObjectTreeMapper(g, root_name="A")

    # Map to ObjectTree
    object_tree = mapper.map_to_object_tree()

    # Get the tree structure for assertions
    tree_structure = object_tree.makeTaggedTree()

    # Print the tree structure for debugging
    print("\nTree structure from test-tree2+bricks.ttl:")
    for node, data in sorted(tree_structure.items()):
      print(f"{node}: {data}")

    # Print all nodes in the tree
    print("\nAll nodes in the tree:", sorted(tree_structure.keys()))

    # Print all triples for reference
    print("\nAll triples in the graph:")
    for s, p, o in g:
      print(f"{s} {p} {o}")

    # Check that all expected nodes are in the tree
    expected_nodes = ['A', 'Aa', 'Ab', 'Aba', 'Bb', 'Bbb', 'Bbc', 'I', 'Sa', 'Sb', 'Uri']
    missing_nodes = [node for node in expected_nodes if node not in tree_structure]

    if missing_nodes:
      print(f"\nMissing nodes: {missing_nodes}")

    # Check each expected node
    for node in expected_nodes:
      self.assertIn(node, tree_structure, f"Node '{node}' should exist in the tree")

    # Check specific relationships
    if 'A' in tree_structure and 'Aa' in tree_structure:
      self.assertIn('Aa', tree_structure['A']['children'], "'Aa' should be a child of 'A'")
    if 'A' in tree_structure and 'Ab' in tree_structure:
      self.assertIn('Ab', tree_structure['A']['children'], "'Ab' should be a child of 'A'")
    if 'Ab' in tree_structure and 'Aba' in tree_structure:
      self.assertIn('Aba', tree_structure['Ab']['children'], "'Aba' should be a child of 'Ab'")

    # Verify some key relationships
    self.assertIn('Aa', tree_structure['A']['children'], "'Aa' should be a child of 'A'")
    self.assertIn('Ab', tree_structure['A']['children'], "'Ab' should be a child of 'A'")
    self.assertIn('Bb', tree_structure['A']['children'], "'Bb' should be a child of 'A'")

    # Verify leaf nodes
    self.assertEqual(tree_structure['Sa']['children'], [], "'Sa' should be a leaf node")
    self.assertEqual(tree_structure['Sb']['children'], [], "'Sb' should be a leaf node")
    self.assertEqual(tree_structure['Uri']['children'], [], "'Uri' should be a leaf node")
    self.assertEqual(tree_structure['Bbc']['children'], [], "'Bbc' should be a leaf node")
    self.assertEqual(tree_structure['I']['children'], [], "'I' should be a leaf node")

    # Verify some ancestor relationships
    self.assertEqual(tree_structure['Aa']['ancestors'], ['A'], "'Aa' should have 'A' as ancestor")
    self.assertIn('A', tree_structure['Bbb']['ancestors'], "'Bbb' should have 'A' as ancestor")
    self.assertIn('Bb', tree_structure['Bbb']['ancestors'], "'Bbb' should have 'Bb' as ancestor")


if __name__ == "__main__":
  unittest.main()