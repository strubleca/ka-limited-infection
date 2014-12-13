###
# For Documentation
###
__author__  = 'Craig Struble <strubleca@yahoo.com>'
__date__    = 'December 13, 2014'
__version__ = '1'

import graph # Our basic graph implementation
import json
from optparse import OptionParser

class User(graph.Node):
    """Model users as graph nodes with some special methods."""

    def __init__(self, id, features=set()):
        """Initialize a user with a set of features."""
        _features = set() | features
        super(User, self).__init__(id, _features)

    def features(self):
        """Return the features this user has."""
        return self.data()

    def add_feature(self, feature):
        """Add a web site feature to this user."""
        self.data().add(feature)

    def discard_feature(self, feature):
        """Discard a feature from this user."""
        self.data().discard(feature)

    def coaches(self):
        """Return the set of users this user coaches"""
        return self.outgoing()

    def is_coached_by(self):
        """Return the set of users this user is coached by"""
        return self.incoming()

def total_infection(coaching_graph, initial_user_id, feature):
    """Totally infect a coaching graph with a feature from the initial user"""
    infected = coaching_graph.connected_component(initial_user_id)
    discard = feature.startswith("!")
    for user in infected:
        if discard:
            user.discard_feature(feature[1:]) # strip the leading !
        else:
            user.add_feature(feature)

def json_graph_to_coaching_graph(graph_file):
    """Convert JSON encoded graph to a coaching graph."""
    graph_data = json.load( open(graph_file) )
    coaching_graph = graph.Graph(directed=True)

    # Add users to the coaching graph
    for user_id in graph_data["users"]:
        user = User(user_id)
        coaching_graph.add_node(user)

    # Add coaching relationships
    coaches = graph_data["coaches"]
    for coach_id in coaches.keys():
        coach = coaching_graph.find_node(coach_id)
        for student_id in coaches[coach_id]:
            student = coaching_graph.find_node(student_id)
            coaching_graph.add_edge(coach, student)

    return coaching_graph

def print_user_features(coaching_graph):
    """Print the features each user of coaching_graph has"""

    for user in coaching_graph.nodes():
        print "User %s has features %s" % (user.id(), user.features())


def main(graph_file):
    """Main script to execute"""

    coaching_graph = json_graph_to_coaching_graph(graph_file)
    print coaching_graph

    total_infection(coaching_graph, "A", "login")
    print_user_features(coaching_graph)

    total_infection(coaching_graph, "B", "points")
    print_user_features(coaching_graph)

    total_infection(coaching_graph, "M", "home")
    print_user_features(coaching_graph)

    total_infection(coaching_graph, "D", "!points")
    print_user_features(coaching_graph)

# Execute main script if this file is called for execution
if __name__ == "__main__":
    usage = "usage: %prog filename"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("missing output file name")

    main(args[0])
