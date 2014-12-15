###############################################################################
# Draw a coaching graph using the graph-tool Python package
###############################################################################

#------------------------------------------------------------------------------
# Various informative variables for documentation.
#------------------------------------------------------------------------------
__author__  = 'Craig Struble <strubleca@yahoo.com>'
__date__    = 'December 14, 2014'
__version__ = '1'

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------
from graph_tool.all import *
from argparse import ArgumentParser
from pylab import *
import json

def json_file_to_graph_tool(graph_file):
    """Convert JSON encoded graph to a graph-tool."""
    graph_data = json.load( open(graph_file) )
    coaching_graph = Graph(directed=True)
    users = dict()
    uids = coaching_graph.new_vertex_property("string")
    version = coaching_graph.new_vertex_property("int")
    coaching_graph.vertex_properties["id"] = uids
    coaching_graph.vertex_properties["version"] = version

    # Add users to the coaching graph
    for user_id in graph_data["users"]:
        user = coaching_graph.add_vertex()
        uids[user] = user_id
        users[user_id] = user

    # Add coaching relationships
    coaches = graph_data["coaches"]
    for coach_id in coaches.keys():
        coach = users[coach_id]
        for student_id in coaches[coach_id]:
            student = users[student_id]
            coaching_graph.add_edge(coach, student)

    # Add features to users if available
    if "features" in graph_data:
        features = graph_data["features"]
        for user_id in features.keys():
            user = users[user_id]
            if len(features[user_id]) > 0:
                version[user] = sum([int(x) for x in features[user_id]])
            else:
                version[user] = 0

    return coaching_graph

def main(args):
    """Main script"""
    coaching_graph = json_file_to_graph_tool(args.infilename)

    pos = sfdp_layout(coaching_graph)
    version = coaching_graph.vertex_properties["version"]
    graph_draw(coaching_graph, pos, output_size=(1000, 1000), 
           vertex_color=[0,0,0,0.75],
           vertex_fill_color=version, vertex_size=10, edge_pen_width=1.2,
           vcmap=matplotlib.cm.seismic, output=args.outfilename)

if __name__ == "__main__":
    parser = ArgumentParser(description="Draw a coaching graph.")
    parser.add_argument('infilename',  
            help="input file containing coaching graph")
    parser.add_argument('outfilename',
            help="output file containing graph drawing")
    args = parser.parse_args()

    main(args)
