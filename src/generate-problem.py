
import random
import yaml
import networkx as nx

import argparse

def grid_2d_graph(m,n,percent_drop=0.0,create_using=nx.DiGraph()):
    """ Return the 2d grid graph of mxn nodes,
        each connected to its nearest neighbors.
        Optional argument periodic=True will connect
        boundary nodes via periodic boundary conditions.
    """
    G=nx.empty_graph(0,create_using)
    G.name="grid_2d_graph"
    rows=range(m)
    columns=range(n)
    G.add_nodes_from( 'waypoint{}{}'.format(i,j) for i in rows for j in columns )

    G.add_edges_from( ('waypoint{}{}'.format(i,j),'waypoint{}{}'.format(i-1,j)) for i in rows for j in columns if i>0 )
    G.add_edges_from( ('waypoint{}{}'.format(i,j),'waypoint{}{}'.format(i,j-1)) for i in rows for j in columns if j>0 )
    if G.is_directed():
        G.add_edges_from( ('waypoint{}{}'.format(i,j),'waypoint{}{}'.format(i+1,j)) for i in rows for j in columns if i<m-1 )
        G.add_edges_from( ('waypoint{}{}'.format(i,j),'waypoint{}{}'.format(i,j+1)) for i in rows for j in columns if j<n-1 )
    else:
        print('not directed?')



    edges_to_drop = int(len(G.edges()) * percent_drop)
    for i in range(edges_to_drop):
        # pick random node
	node = random.sample(list(G.nodes()), 1)
	edges = list(G.edges(node))
        print(len(edges))
	if len(edges) > 1:
            # remove both 'directions' of the edge
            edge = edges[0]
            G.remove_edge(edge[0], edge[1])
            G.remove_edge(edge[1], edge[0])

    G.add_edges_from( ('waypoint{}{}'.format(i,j),'waypoint{}{}'.format(i,j)) for i in rows for j in columns )
    return G

def save_yaml(error, gridsize, percent_drop, filename):
    
    data = {}

    data['types'] = ['uav', 'rover']
    data['agents'] = [
        ['a0', 'uav'],
        ['a1', 'rover'],
        ['a2', 'uav']
    ]


    data['error'] = error


    g = grid_2d_graph(gridsize[0], gridsize[1], percent_drop=percent_drop)
    n = list(g.nodes())
    e = g.edges()

    #nodes_to_drop = 0 # no removal for now, what is going on???

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
    save_yaml(float(args.error),(int(args.grid_x), int(args.grid_y)), float(args.drop_percent),args.output)
    

if __name__ == "__main__":
    main()
