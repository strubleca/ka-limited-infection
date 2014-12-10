###############################################################################
###############################################################################
"""Basic graph ADT"""

class Node:
    """A representation of graph nodes."""

    def __init__(self, id, data, neighbors=set()):
        self._id = id
        self._data = data
        self._neighbors = neighbors
        self._visited = False

    def neighbors(self):
        """Return the collection of neighbors"""
        return self._neighbors

    def add_neighbor(self, node):
        """Add a neighboring node."""
        self._neighbors.add(node)

    def visited(self):
        """Return the visited state of the node"""
        return self._visited

    def set_visited(self, value=False):
        """Set the visited state of the node"""
        self._visited = valse

class Graph:
    """A representation of graphs as a collection of nodes."""

    def __init__(self, directed=False):
        self._nodes = set()
        self._directed = directed

    def add_node(self, node):
        """Add a node to the graph."""
        self._nodes.add(node)

    def add_edge(self, node1, node2):
        """Add an edge to the graph.

        Adding an edge makes node2 a neighbor of node1. If the graph
        is undirected, node1 will be a neighbor of node2 as well.
        """
        self.add_node(node1)
        self.add_node(node2)
        node1.add_neighbor(node2)
        if not self._directed:
            node2.add_neigbor(node1)

    def connected_component(self, start):
        """Return the connected component containing start.
        
        Finds all nodes in the (weakly) connected component containing the
        node start. For undirected graphs, this corresponds to the
        (strongly) connected component.

        This is implemented using a breadth first search.
        """
        if start not in self._nodes:
            raise Exception("Starting node not in graph.")

        # Initialize the visited state of all nodes.
        for node in self._nodes:
            node.set_visited(False)

        # Breadth first search starting at start.
        connected = []           # The list of nodes in the connected component
        node_queue = deque()     # A queue of nodes to visit in the bfs
        node_queue.append(start) # Initialize with starting node
        while len(node_queue) > 0:
            current_node = node_queue.popleft()
            connected.append(current_node)
            if not current_node.visited():
                node_queue.extend(current_node.neighbors())
                current_node.set_visited(True)

        return connected
