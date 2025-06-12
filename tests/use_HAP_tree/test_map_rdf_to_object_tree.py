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
        
        # Add the node to the tree if it's not already there
        if node_name not in tree["nodes"] and parent is not None:
            # Only add the node if it's not the root (which is already added)
            tree.addChildtoNode(node_name, parent)
        
        # Find all members of this node
        for s, p, o in self.graph.triples((node, RDFS.member, None)):
            self._build_tree_recursive(tree, o, node_name, visited)
            
        # Also process inverse member relationships
        for s, p, o in self.graph.triples((None, RDFS.member, node)):
            s_name = self._get_name_from_uri(s)
            if s_name not in tree["nodes"] and s_name != node_name:  # Prevent self-reference
                tree.addChildtoNode(s_name, node_name)
                
        # Process boolean values (xsd:boolean predicates)
        for s, p, o in self.graph.triples((None, XSD.boolean, None)):
            # Get the name of the boolean property (Sa or Sb)
            bool_prop = str(o).split('#')[-1]
            # Get the value of the boolean (Aa or Ab)
            for _, _, value in self.graph.triples((o, RDF.value, None)):
                value_name = str(value).split('#')[-1]
                # Add the boolean property as a child of its value
                if bool_prop not in tree["nodes"] or tree["nodes"][bool_prop] != value_name:
                    tree.addChildtoNode(bool_prop, value_name)
    
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
            print(s,p,o)
        
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

if __name__ == "__main__":
    unittest.main()
