###############################################################################
# Infect coaching graphs in a variety of ways.
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
import graph # Our basic graph implementation
import json
from collections import deque
from argparse import ArgumentParser

#------------------------------------------------------------------------------
# User Model
#------------------------------------------------------------------------------
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

    def update_feature(self, feature):
        """Adds or discards a feature. Discards if feature starts with !"""
        if feature.startswith("!"):
            self.discard_feature(feature[1:]) # remove the leading !
        else:
            self.add_feature(feature)

    def coaches(self):
        """Return the set of users this user coaches"""
        return self.outgoing()

    def is_coached_by(self):
        """Return the set of users this user is coached by"""
        return self.incoming()

#------------------------------------------------------------------------------
# Functions for performing infections
#------------------------------------------------------------------------------
def total_infection(coaching_graph, feature, initial_user_id):
    """Totally infect a coaching graph component with a feature"""
    infected = coaching_graph.connected_component(initial_user_id)
    for user in infected:
        user.update_feature(feature)

def trim_infections(infections, delta):
    """Trim the list of infections so that they are a factor of delta apart."""

    trimmed = [infections[0]] # Should always be the empty set.
    y = [float(len(x)) for x in infections]
    last = y[0]
    for i in range(1,len(y)):
        if y[i] > last * (1.0 + delta):
            trimmed.append(infections[i])
            last = y[i]

    return trimmed

def approx_component_infection(coaching_graph, min_users, max_users):
    """Find a collection of components to infect, getting to min_users."""

    # This uses an approach similar to the approximate subset sum
    # algorithm. A list of potentially acceptable collections is
    # maintained, removing any that get too large and trimming
    # infections that are too close in size. This approach is
    # guaranteed to find at least one infection within the range
    # if one exists.
    #
    # The speed of this approach depends on the min and max number 
    # of users. The bigger the range, the faster this is likely to be.
    # The closer we're required to be to the exact answer, the more 
    # candidate infections need to be maintained (i.e. less trimming 
    # allowed) and the more memory is used as well.
    seeds = coaching_graph.all_connected_components()
    epsilon = (float(max_users) / min_users) - 1.0
    n = len(seeds)

    infections = [set()] # Start with the empty set
    for seed in seeds:
        new_infections = [x | set(seed) for x in infections]
        new_infections = filter(lambda x : len(x) <= max_users, new_infections)
        infections.extend(new_infections)
        infections.sort(key=lambda x : len(x))
        infections = trim_infections(infections, epsilon / (2.0 * n))

    return infections.pop()


def approx_class_infection(coaching_graph, seeds, min_users, max_users):
    """Find a collection of users to infect, starting with seeds"""

    # This uses an approach similar to the approximate subset sum
    # algorithm. A list of potentially acceptable collections is
    # maintained, removing any that get too large and trimming
    # infections that are too close in size. This approach is
    # guaranteed to find at least one infection within the range
    # if one exists.
    #
    # The speed of this approach depends on the min and max number 
    # of users. The bigger the range, the faster this is likely to be.
    # The closer we're required to be to the exact answer, the more 
    # candidate infections need to be maintained (i.e. less trimming 
    # allowed) and the more memory is used as well.
    epsilon = (float(max_users) / min_users) - 1.0
    n = len(seeds)

    infections = [set()] # Start with the empty set
    for seed in seeds:
        new_infections = [x | set([seed]) | set(seed.coaches()) 
                for x in infections]
        new_infections = filter(lambda x : len(x) <= max_users, new_infections)
        infections.extend(new_infections)
        infections.sort(key=lambda x : len(x))
        infections = trim_infections(infections, epsilon / (2.0 * n))

    return infections.pop()

def limited_infection(coaching_graph, feature, min_users, max_users):
    """Perform a limited infection, between minimum and maximum users.

    Limited infections first infect entire components then infect
    classes, starting with coaches and their students (ignoring
    transitivity and "is coached by" relationships). If a limited infection
    exists between the minimum and maximum number of users (inclusive), 
    it will be performed.
    
    Returns True if the infection was successful, False otherwise.
    """

    users = approx_component_infection(coaching_graph, min_users, max_users)
    if len(users) < min_users:
        # Component infection didn't infect enough users. Move to class
        # infections.
        seeds = coaching_graph.all_parents() | coaching_graph.all_singletons()
        seeds -= users # Remove already infected users.
        min_class_users = min_users - len(users)
        max_class_users = max_users - len(users)
        class_users = approx_class_infection(coaching_graph, seeds, 
                min_class_users, max_class_users)
        users |= class_users

    if len(users) >= min_users:
        for user in users:
            user.update_feature(feature)
        return True

    return False

def exact_subset_sum(sizes, target, i, n, subtotal):
    """Solve the subset sum problem recursively."""
    if subtotal == target:
        return [i]
    elif subtotal > target:
        # Optimization. Stop considering this possible solution.
        return False

    j = i + 1
    while j < n:
        ret = exact_subset_sum(sizes, target, j, n, subtotal + sizes[j])
        if ret != False:
            if i > -1:
                ret.append(i)
            return ret
        j = j + 1

    return False

def exact_limited_infection(coaching_graph, feature, num_users):
    """Infect a specified number of users exactly in a coaching graph."""
    components = coaching_graph.all_connected_components()
    sizes = [len(x) for x in components]
    solution = exact_subset_sum(sizes, num_users, -1, len(sizes), 0)
    if solution != False:
        for i in solution:
            for user in components[i]:
                user.update_feature(feature)
        return True
    else:
        return False

#------------------------------------------------------------------------------
# Input output functions
#------------------------------------------------------------------------------
def json_file_to_coaching_graph(graph_file):
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

    # Add features to users if available
    if "features" in graph_data:
        features = graph_data["features"]
        for user_id in features.keys():
            user = coaching_graph.find_node(user_id)
            for feature in features[user_id]:
                user.add_feature(feature)

    return coaching_graph

def coaching_graph_to_json_file(coaching_graph, graph_file):
    """Convert a coaching graph to a JSON file."""

    output = dict()
    # users
    output['users'] = [x.id() for x in coaching_graph.nodes()]

    # coaching relationships
    coaches = coaching_graph.all_parents()
    coaching = dict()
    for coach in coaches:
        coaching[coach.id()] = [x.id() for x in coach.coaches()]
    output['coaches'] = coaching

    # Features for users
    features = dict()
    for user in coaching_graph.nodes():
        features[user.id()] = list(user.features())
    output['features'] = features

    # Output to a file
    json.dump(output, open(graph_file, "w"), indent=4)

def print_user_features(coaching_graph):
    """Print the features each user of coaching_graph has"""

    for user in coaching_graph.nodes():
        print "User %s has features %s" % (user.id(), user.features())

def main(args):
    """Main script to execute"""

    coaching_graph = json_file_to_coaching_graph(args.infilename)

    if args.total_infection:
        total_infection(coaching_graph, args.feature, args.total_infection)

    if args.limited_infection:
        limited_infection(coaching_graph, args.feature, 
                args.limited_infection[0], args.limited_infection[1])

    if args.exact_infection:
        exact_limited_infection(coaching_graph, args.feature, 
                args.exact_infection)

    coaching_graph_to_json_file(coaching_graph, args.outfilename)

#------------------------------------------------------------------------------
# Main script
#------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = ArgumentParser(description="Infect a coaching graph.")
    parser.add_argument('feature', 
            help="infect the graph with this feature")
    parser.add_argument('infilename',  
            help="input file containing coaching graph")
    parser.add_argument('outfilename',
            help="output file containing infected graph")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--exact-infection", 
            type=int,
            metavar='NUM',
            help="infect exactly NUM users if possible")
    group.add_argument("-l", "--limited-infection", nargs=2, 
            type=int,
            metavar=('MIN', 'MAX'),
            help="infect MIN to MAX users if possible")
    group.add_argument("-t", "--total-infection", 
            metavar='USER',
            help="totally infect the component containing USER")
    args = parser.parse_args()

    main(args)
