import networkx as nx
import random as rd
import argparse
import os


'''
Returns two non-isorphic graphs h1,h2 of size n which are each generated from a tree 
by appending a single edge, such that their sets of vertex degrees are equivalent.
'''
def blockgraph_layouts(n):

    while True:
        # generate random tree g of size n
        g = nx.random_tree(n=n)

        # group vertices by their degrees
        deg_grouped = {}
        for i,d in g.degree():
            if d in deg_grouped: deg_grouped[d].append(i)
            else: deg_grouped[d] = [i]

        # find two vertex pairs (v1,v2) and (u1,u2) with d(v1)==d(u1) and d(v2)==d(u2)
        delete = [key for key in deg_grouped if len(deg_grouped[key])<2]
        for key in delete: del deg_grouped[key]
        if not deg_grouped: continue
        deg1 = rd.choice(list(deg_grouped.values()))
        v1,u1 = rd.sample(deg1, 2)
        deg1.remove(v1)
        deg1.remove(u1)
        delete = [key for key in deg_grouped if len(deg_grouped[key])<2]
        for key in delete: del deg_grouped[key]
        if not deg_grouped: continue
        deg2 = rd.choice(list(deg_grouped.values()))
        v2,u2 = rd.sample(deg2, 2)

        # check whether extra edges are already contained in g
        if (v1,v2) in g.edges: continue
        if (u1,u2) in g.edges: continue

        # generate networkx graphs
        h1 = g.copy()
        h1.add_edge(v1,v2)
        h2 = g.copy()
        h2.add_edge(u1,u2)

        # return graphs only if they are non-isomorphic
        if not nx.is_isomorphic(h1,h2): return h1,h2


'''
Returns block graph that has the underlying structure of graph g. Each node in g is replaced
by a block of c vertices. vertices within each block and of neighboring blocks are connected
with probability p. Additionally a number of m noise edges are added. 
'''
def blockgraph(g, c, p, m):

    edges = []

    # intra cluster nodes
    for v in g.nodes:
        for i in range(c):
            for j in range(i):
                if rd.random() < p:
                    edges.append((v*c+j,v*c+i))

    # inter cluster nodes
    for v in g.nodes:
        for u in g.neighbors(v):
            if v<u:
                for i in range(c):
                    for j in range(c):
                        if rd.random() < p:
                            edges.append((v*c+j,u*c+i))

    # random edges
    nmb_edges = len(edges)
    while len(edges) < nmb_edges+m:
        v = rd.randint(0, len(g.nodes)*c-1)
        u = rd.randint(0, len(g.nodes)*c-1)
        u,v = min(u,v), max(u,v)
        if v!=u and (u,v) not in edges: edges.append((v,u))

    # return networkx graph
    h = nx.Graph()
    h.add_nodes_from(range(len(g.nodes)*c))
    h.add_edges_from(edges)
    return h
    

'''
Writes graphs to file following TU Dortmund format.
'''
def write_graphs(graphs, file_name):

    if not os.path.exists(file_name):
        os.mkdir(file_name)

    f_A = open(file_name+'/'+file_name+'_A.txt', 'w')
    f_gi = open(file_name+'/'+file_name+'_graph_indicator.txt', 'w')
    f_gl = open(file_name+'/'+file_name+'_graph_labels.txt', 'w')
    f_A.close()
    f_gi.close()
    f_gl.close()

    f_A = open(file_name+'/'+file_name+'_A.txt', 'a')
    f_gi = open(file_name+'/'+file_name+'_graph_indicator.txt', 'a')
    f_gl = open(file_name+'/'+file_name+'_graph_labels.txt', 'a')

    offset = 1
    for i,g in enumerate(graphs):
        for (u,v) in g.edges:
            f_A.write(str(offset+v)+', '+str(offset+u)+'\n')
            f_A.write(str(offset+u)+', '+str(offset+v)+'\n')
        for v in g.nodes:   
            f_gi.write(str(i+1)+'\n')
        f_gl.write(str(i%2)+'\n')
        offset += len(g.nodes)

    f_A.close()
    f_gi.close()
    f_gl.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Blockgraph Dataset Generator')
    parser.add_argument('--name', 
                        type=str, 
                        required=True, 
                        help='Name of output file(s)')
    parser.add_argument('--N', 
                        type=int, 
                        required=True, 
                        help='Number of graphs per class')
    parser.add_argument('--n', 
                        type=int, 
                        required=True, 
                        help='Number of blocks')
    parser.add_argument('--c', 
                        type=int, 
                        required=True, 
                        help='Size of blocks')
    parser.add_argument('--p', 
                        type=float, 
                        required=True, 
                        help='Edge probability')
    parser.add_argument('--m', 
                        type=int, 
                        required=True, 
                        help='Number of noise edges')
    parser.add_argument('--seed', 
                        type=int, 
                        required=False, 
                        default=None, 
                        help='Random seed')
    args = parser.parse_args()
    
    file = args.name
    N = args.N
    n = args.n
    c = args.c
    p = args.p
    m = args.m
    if args.seed: rd.seed(args.seed)

    # generate underlying block graph structures
    g,h = blockgraph_layouts(n)

    # generate N blockgraphs for each structure
    graphs = []
    for _ in range(N):
        graphs.append(blockgraph(g, c, p, m))
        graphs.append(blockgraph(h, c, p, m))

    # write graphs to file
    write_graphs(graphs, file)
