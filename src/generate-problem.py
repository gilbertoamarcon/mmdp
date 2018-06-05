
import random
import yaml
import networkx as nx

import argparse

def grid_2d_graph(m,n,create_using=nx.DiGraph()):
    """ Return the 2d grid graph of mxn nodes,
        each connected to its nearest neighbors.
        Optional argument periodic=True will connect
        boundary nodes via periodic boundary conditions.
    """
    G=nx.empty_graph(0,create_using)
    G.name="grid_2d_graph"
    rows=range(m)
    columns=range(n)
    G.add_nodes_from( 'waypoint_{}_{}'.format(i,j) for i in rows for j in columns )
    G.add_edges_from( ('waypoint_{}_{}'.format(i,j),'waypoint_{}_{}'.format(i-1,j)) for i in rows for j in columns if i>0 )
    G.add_edges_from( ('waypoint_{}_{}'.format(i,j),'waypoint_{}_{}'.format(i,j-1)) for i in rows for j in columns if j>0 )
    if G.is_directed():
        G.add_edges_from( ('waypoint_{}_{}'.format(i,j),'waypoint_{}_{}'.format(i+1,j)) for i in rows for j in columns if i<m-1 )
        G.add_edges_from( ('waypoint_{}_{}'.format(i,j),'waypoint_{}_{}'.format(i,j+1)) for i in rows for j in columns if j<n-1 )
    return G

def save_yaml(error, gridsize, percent_drop, filename):
    error = 0.1
    gridsize = 3, 2
    percent_drop = .3
    
    data = {}

    data['types'] = ['uav', 'rover']
    data['agents'] = [
        ['a0', 'uav'],
        ['a1', 'rover'],
        ['a2', 'uav']
    ]


    data['error'] = error

    g = grid_2d_graph(gridsize[0], gridsize[1])
    n = list(g.nodes())
    e = g.edges()

    nodes_to_drop = int(len(e) * percent_drop)

    for i in range(nodes_to_drop):
        # pick random node
	node = random.sample(n, 1)
	edges = g.edges(node)
	edges = list(edges)
	if len(edges) > 1:
            g.remove_edge(*edges[0])


    data['locs'] = n
    edges = list(g.edges())
    edges = [list(x) for x in edges]
    data['roads'] = edges

    goals = random.sample(n, 2)
    
    data['goal'] = {
        goals[0]: [
            'uav',
    	'rover'
        ],
        goals[1]: [
            'uav'
        ],
    }
    
    with open(filename, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def main():
    # Parsing user input
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e','--error',
        nargs='?',
        required=True,
        help='Allowed solution error (decimal).'
    )
    parser.add_argument(
        '-o','--output',
        nargs='?',
        required=True,
        help='Output problem file (YAML filename).'
    )
    parser.add_argument(
        '-x','--grid_x',
        nargs='?',
        required=True,
        help='grid width'
    )
    parser.add_argument(
        '-y','--grid_y',
        nargs='?',
        required=True,
        help='grid height'
    )
    parser.add_argument(
        '-d','--drop_percent',
        nargs='?',
        required=True,
        help='percentage of edges to drop from the node'
    )
    args = parser.parse_args()
    save_yaml(args.error,(args.grid_x, args.grid_y), args.drop_percent,args.output)
    

if __name__ == "__main__":
    main()
