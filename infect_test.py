###############################################################################
# Unit tests for graph and infection code.
###############################################################################

import graph
import infect
import unittest

class TestGraphFunctions(unittest.TestCase):
    """Unit testing of basic graph functionality."""

    def setUp(self):
        """Setup for unit testing of graph functionality."""
        node_data = {"key1" : 1}
        self.node = graph.Node("A", node_data)

    def test_new_node(self):
        """Test new node methods."""
        self.assertEqual(self.node.id(), "A")
        self.assertEqual(len(self.node.incoming()), 0)
        self.assertEqual(len(self.node.outgoing()), 0)
        self.assertEqual(len(self.node.neighbors()), 0)

    def test_incoming(self):
        """Test incoming methods."""

        node1 = graph.Node("A", [])
        node2 = graph.Node("B", [])
        node1.add_incoming(node2)
        self.assertEqual(node1.incoming(), set([node2]))
        self.assertEqual(len(node2.outgoing()), 0) # is not modified

    def test_outgoing(self):
        """Test outgoing methods."""

        node1 = graph.Node("A", [])
        node2 = graph.Node("B", [])
        node1.add_outgoing(node2)
        self.assertEqual(node1.outgoing(), set([node2]))
        self.assertEqual(len(node2.incoming()), 0) # is not modified

    def test_neighbors(self):
        """Test neighbors method."""
        node1 = graph.Node("A", [])
        node2 = graph.Node("B", [])
        node3 = graph.Node("C", [])

        # Note, the below ONLY modifies node1
        node1.add_incoming(node2)
        node1.add_outgoing(node3)

        # Neighbors should be both incoming and outgoing nodes
        self.assertEqual(len(node1.neighbors()), 2)
        self.assertEqual(node1.neighbors(), node1.incoming() | node1.outgoing())

    def test_graph_creation(self):
        """Test graph creation"""

        graph1 = graph.Graph(directed=True)
        node1 = graph.Node("A", [])
        node2 = graph.Node("B", [])
        node3 = graph.Node("C", [])

        graph1.add_node(node1)
        graph1.add_node(node2)
        graph1.add_node(node3)
        self.assertTrue(len(graph1.nodes()), 3)

        # Create a loop
        graph1.add_edge(node1, node2)
        graph1.add_edge(node2, node3)
        graph1.add_edge(node3, node1)

        # Test the edges
        self.assertEquals(node1.outgoing(), set([node2]))
        self.assertEquals(node1.incoming(), set([node3]))

        # Make sure not to find nodes not in the graph
        with self.assertRaises(KeyError) as cm:
                graph1.find_node("X")


    # TODO(strubleca@yahoo.com): Add more unit tests for graph functions.


class TestInfectFunctions(unittest.TestCase):
    """Unit testing of infection functionality."""

    def setUp(self):
        """Setup for unit testing"""
        self.graph1 = infect.json_file_to_coaching_graph("graphs/graph1.json")
        self.graph2 = infect.json_file_to_coaching_graph("graphs/graph2.json")
        self.graph3 = infect.json_file_to_coaching_graph("graphs/graph3.json")

    def test_load(self):
        """Test graph loading"""
        self.assertEqual(len(self.graph1.nodes()), 4)
        self.assertEqual(len(self.graph2.nodes()), 9)
        self.assertEqual(len(self.graph3.nodes()), 13)

        nodeA = self.graph1.find_node("A")
        self.assertEqual(len(nodeA.coaches()), 3)
        self.assertEqual(len(nodeA.is_coached_by()), 0)
        nodeB = self.graph1.find_node("B")
        self.assertEqual(nodeB.is_coached_by(), set([nodeA]))

    def test_feature_update(self):
        """Test the update_feature. Also tests add_feature/disable_feature"""

        nodeA = self.graph1.find_node("A")
        nodeA.update_feature("test_feature")
        self.assertTrue("test_feature" in nodeA.features())

        nodeA.update_feature("!test_feature")
        self.assertTrue("test_feature" not in nodeA.features())

    def test_total_infection(self):
        """Test total_infection function"""

        # Simple infection from coach
        infect.total_infection(self.graph1, "coach", "A")
        for node in self.graph1.nodes():
            self.assertTrue("coach" in node.features())

        # Simple infection from student
        infect.total_infection(self.graph1, "student", "C")
        for node in self.graph1.nodes():
            self.assertTrue("student" in node.features())

        # Transitivity
        infect.total_infection(self.graph2, "transitive", "A")
        for node in self.graph2.nodes():
            self.assertTrue("transitive" in node.features())

        # Multiple components
        infect.total_infection(self.graph3, "component1", "A")
        infect.total_infection(self.graph3, "component2", "K")
        for node in self.graph3.nodes():
            if node.id() < "J":
                self.assertTrue("component1" in node.features()
                        and "component2" not in node.features())
            else:
                self.assertTrue("component2" in node.features()
                        and "component1" not in node.features())


    def test_limited_infection(self):
        """Test the limited_infection function"""

        # Simple case
        success = infect.limited_infection(self.graph1, "limited1", 1, 5)
        self.assertTrue(success)

        # All nodes should be infected
        for node in self.graph1.nodes():
            self.assertTrue("limited1" in node.features())

        # Make it fail because we can't get in range
        success = infect.limited_infection(self.graph1, "limited2", 5, 10)
        self.assertFalse(success)
        for node in self.graph1.nodes():
            self.assertTrue("limited2" not in node.features())

        # Infect a subset of nodes within the range, but not the whole
        # graph, which is a single component.
        success = infect.limited_infection(self.graph2, "limited3", 4, 8)
        self.assertTrue(success)
        num_infected = len(filter(lambda x : "limited3" in x.features(), 
            self.graph2.nodes()))
        self.assertTrue(num_infected >= 4 and num_infected <= 8)
        self.assertTrue(num_infected < len(self.graph2.nodes()))

        # Infect the small component, but not the large one.
        success = infect.limited_infection(self.graph3, "limited4", 3, 5)
        self.assertTrue(success)
        for node in self.graph3.nodes():
            if node.id() < "J":
                self.assertTrue("limited4" not in node.features())
            else:
                self.assertTrue("limited4" in node.features())

        # Infect the small component, and a few in the large one
        success = infect.limited_infection(self.graph3, "limited5", 3, 8)
        self.assertTrue(success)
        for node in self.graph3.nodes():
            if node.id() >= "J":
                self.assertTrue("limited5" in node.features())
        num_infected = len(filter(lambda x : "limited5" in x.features(), 
            self.graph3.nodes()))
        self.assertTrue(num_infected >= 4 and num_infected <= 8)
        self.assertTrue(num_infected < len(self.graph3.nodes()))

        # Infect everything
        success = infect.limited_infection(self.graph3, "limited6", 11, 15)
        self.assertTrue(success)
        for node in self.graph3.nodes():
            self.assertTrue("limited6" in node.features())

    def test_exact_infection(self):
        """Test the exact_limited_infection"""

        # First a failure
        success = infect.exact_limited_infection(self.graph1, "exact1", 3)
        self.assertFalse(success)
        for node in self.graph1.nodes():
            self.assertTrue("exact1" not in node.features())

        # Now a success
        success = infect.exact_limited_infection(self.graph1, "exact2", 4)
        self.assertTrue(success)
        for node in self.graph1.nodes():
            self.assertTrue("exact2" in node.features())

        # Now a failure with multiple components
        success = infect.exact_limited_infection(self.graph3, "exact3", 6)
        self.assertFalse(success)
        for node in self.graph3.nodes():
            self.assertTrue("exact3" not in node.features())

        # Now successes for each component and both combined
        success = infect.exact_limited_infection(self.graph3, "exact4", 4)
        self.assertTrue(success)
        for node in self.graph3.nodes():
            if node.id() < "J":
                self.assertTrue("exact4" not in node.features())
            else:
                self.assertTrue("exact4" in node.features())

        success = infect.exact_limited_infection(self.graph3, "exact5", 9)
        self.assertTrue(success)
        for node in self.graph3.nodes():
            if node.id() < "J":
                self.assertTrue("exact5" in node.features())
            else:
                self.assertTrue("exact5" not in node.features())

        success = infect.exact_limited_infection(self.graph3, "exact6", 13)
        self.assertTrue(success)
        for node in self.graph3.nodes():
            self.assertTrue("exact6" in node.features())

if __name__ == "__main__":
    unittest.main()
