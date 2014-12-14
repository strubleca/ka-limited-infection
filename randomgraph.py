###############################################################################
# Create random coaching graphs.
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
import graph
import infect
import random
from argparse import ArgumentParser

#------------------------------------------------------------------------------
# Function for creating random graphs
#------------------------------------------------------------------------------
def random_coaching_graph(num_classes, min_size, max_size, existing_rate):
    """Create a random coaching graph.

    This creates a random coaching graph consisting of num_classes
    in the given size range. A small probability is provided for
    including an existing user in a class instead of creating
    a new user.
    """

    n = 0
    coaching_graph = graph.Graph(directed=True)
    for i in range(num_classes):
        n += 1
        class_size = random.randint(min_size, max_size)
        coach = infect.User(str(n))
        existing_users = coaching_graph.nodes()
        num_existing = len(existing_users)
        coaching_graph.add_node(coach)
        for j in range(class_size):
            if random.uniform(0,1) > existing_rate or num_existing < 100:
                n += 1
                user = infect.User(str(n))
            else:
                user = random.choice(existing_users)

            coaching_graph.add_edge(coach, user)


    return coaching_graph

def main(args):
    """Main script"""

    coaching_graph = random_coaching_graph(args.numclasses,
            args.minsize, args.maxsize, args.existingrate)
    infect.coaching_graph_to_json_file(coaching_graph, args.outfilename)

#------------------------------------------------------------------------------
# Main script
#------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a random coaching graph.")
    parser.add_argument('outfilename',
            help="output file containing infected graph")
    parser.add_argument('numclasses',
            metavar='NUM_CLASS',
            type=int,
            help="number of classes to create")
    parser.add_argument('minsize',
            metavar='MIN_SIZE',
            type=int,
            help="minimum number of students in a class")
    parser.add_argument('maxsize',
            metavar='MAX_SIZE',
            type=int,
            help="maximum number of students in a class")
    parser.add_argument('existingrate',
            metavar='EXISTING_RATE',
            type=float,
            help="rate of existing users to place in a class")

    args = parser.parse_args()
    main(args)
