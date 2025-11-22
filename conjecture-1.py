import networkx as nx
from networkx.algorithms import isomorphism

def load_graphs(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines
    # return [nx.from_graph6_bytes(line.encode()) for line in lines]

def graph6_to_nx(graph6_str):
    return nx.from_graph6_bytes(graph6_str.encode())

subgraphs = load_graphs("subgraphs.txt")
supergraphs = load_graphs("supergraphs.txt")

verbose = False

# Check all combinations
for i, A in enumerate(supergraphs):
    A_comp = nx.complement(graph6_to_nx(A))
    any_match = False
    for j, B in enumerate(subgraphs):
        B_comp = nx.complement(graph6_to_nx(B))
        GM = isomorphism.GraphMatcher(graph6_to_nx(A), graph6_to_nx(B))
        if GM.subgraph_is_isomorphic():
            any_match = True
            if verbose:
                print(f"Supergraph #{i} contains Subgraph #{j}")
                # Optional: print one example mapping
                mapping = next(GM.subgraph_isomorphisms_iter())
                print("  Example mapping:", mapping)
        elif nx.is_isomorphic(A_comp, B_comp):
            any_match = True
            if verbose:
                print(f"Supergraph #{i} contains Subgraph #{j} (in complement)")
        else:
            if verbose:
                print(f"Supergraph #{i} does NOT contain Subgraph #{j}")
    if not any_match:
        print(f"Supergraph #{i} contains NO subgraphs from the list. This is a counterexample.")
        if not verbose:
            break
        
