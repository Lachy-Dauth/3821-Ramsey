import networkx as nx
from networkx.algorithms import isomorphism

def load_graphs(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    return [nx.from_graph6_bytes(line.encode()) for line in lines]

subgraphs = load_graphs("subgraphs.txt")
supergraphs = load_graphs("supergraphs.txt")

# Check all combinations
for i, A in enumerate(supergraphs):
    for j, B in enumerate(subgraphs):
        GM = isomorphism.GraphMatcher(A, B)
        if GM.subgraph_is_isomorphic():
            print(f"Supergraph #{i} contains Subgraph #{j}")
            # Optional: print one example mapping
            mapping = next(GM.subgraph_isomorphisms_iter())
            print("  Example mapping:", mapping)
        else:
            print(f"Supergraph #{i} does NOT contain Subgraph #{j}")
