###############################################################################
# Basic directed graph ADT
###############################################################################

#------------------------------------------------------------------------------
# Various informative variables for documentation.
#------------------------------------------------------------------------------
__author__  = 'Craig Struble <strubleca@yahoo.com>'
__date__    = 'December 13, 2014'
__version__ = '1'

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------
from collections import deque

#------------------------------------------------------------------------------
# Node implementation
#------------------------------------------------------------------------------
class Node(object):
    """A representation of directed graph nodes."""

    def __init__(self, id, data, incoming=set(), outgoing=set()):
        self._id = id
        self._data = data
        self._incoming = set() | incoming
        self._outgoing = set() | outgoing
        self._visited = False

    def __str__(self):
        """An informal string representing nodes"""
        num_incoming = len(self._incoming)
        num_outgoing = len(self._outcoing)
        return "a node with id %s, %d incoming edges and %d outgoing edges" % (
                self._id, num_incoming, num_outgoing)

    def id(self):
        """Return the node's id"""
        return self._id

    def incoming(self):
        """Return nodes with edges coming into this node."""
        return self._incoming

    def outgoing(self):
        """Return nodes with edges coming from this node."""
        return self._outgoing

    def neighbors(self):
        """Return the collection of incoming and outgoing neighbors"""
        return self._incoming | self._outgoing

    def add_incoming(self, node):
        """Add an incoming node."""
        self._incoming.add(node)

    def add_outgoing(self, node):
        """Add an outgoing node."""
        self._outgoing.add(node)

    def visited(self):
        """Return the visited state of the node"""
        return self._visited

    def set_visited(self, value=False):
        """Set the visited state of the node"""
        self._visited = value

    def data(self):
        """Return the data in this node"""
        return self._data

    def set_data(self, data):
        """Update the data in this node"""
        self._data = data

    def is_parent(self):
        """Return whether or not this node has outgoing edges"""
        return len(self._outgoing) > 0

    def is_singleton(self):
        """Return whether or not this node has no neighbors"""
        return len(self.neighbors()) == 0

#------------------------------------------------------------------------------
# Graph implementation
#------------------------------------------------------------------------------
class Graph(object):
    """A representation of graphs as a collection of nodes."""

    def __init__(self, directed=False):
        self._nodes = dict()
        self._directed = directed

    def __str__(self):
        """Return an informal description of the graph"""
        if self._directed:
            graph_type = "directed"
        else:
            graph_type = "undirected"

        n = len(self._nodes)

        return "%s graph with %d nodes" % (graph_type, n)

    def nodes(self):
        """Return the collection of nodes in the graph."""
        return self._nodes.values()

    def add_node(self, node):
        """Add a node to the graph."""
        if node.id() not in self._nodes.keys():  # don't overwrite nodes
            self._nodes[node.id()] = node

    def find_node(self, node_id):
        """Return the node for the given id."""
        return self._nodes[node_id]

    def add_edge(self, node1, node2):
        """Add an edge to the graph.

        Adding an edge makes node2 an outgoing neighbor of node1,
        and node1 an incoming neighbor of node2. If the graph is
        undirected, this also makes node1 an outgoing neighbor of
        node2 and node2 an incoming neighbor of node1.
        """
        self.add_node(node1)
        self.add_node(node2)
        node1.add_outgoing(node2)
        node2.add_incoming(node1)
        if not self._directed:
            node2.add_outgoing(node1)
            node1.add_incoming(node2)

    def connected_component(self, start_id):
        """Return the connected component containing starting node with id.
        
        Finds all nodes in the (weakly) connected component containing the
        node start. 

        This is implemented using a breadth first search.
        """
        if start_id not in self._nodes:
            raise Exception("Starting node not in graph.")

        start = self.find_node(start_id)

        # Initialize the visited state of all nodes.
        for node in self._nodes.values():
            node.set_visited(False)

        # Breadth first search starting at start.
        connected = []           # The list of nodes in the connected component
        node_queue = deque()     # A queue of nodes to visit in the bfs
        node_queue.append(start) # Initialize with starting node
        while len(node_queue) > 0:
            current_node = node_queue.popleft()
            if not current_node.visited():
                connected.append(current_node)
                node_queue.extend(current_node.neighbors())
                current_node.set_visited(True)

        return connected

    def all_connected_components(self):
        """Return an list of lists, each list containing a component."""

        ids = set(self._nodes.keys())
        components = []
        while len(ids) > 0:
            starting_id = ids.pop()
            component = self.connected_component(starting_id)
            ids -= set([x.id() for x in component])
            components.append(component)

        return components

    def all_parents(self):
        """Return a list of nodes that are parents."""

        return set(filter(lambda x : x.is_parent(), 
            self._nodes.itervalues()))

    def all_singletons(self):
        """Return a list of singleton nodes."""

        return set(filter(lambda x : x.is_singleton(), 
            self._nodes.itervalues()))
