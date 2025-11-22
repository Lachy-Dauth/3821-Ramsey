import networkx as nx
from vis import max_degree_difference, visualize_difference, visualize_graph6_diff


def load_graphs(filename):
    """Load graph6 strings from a text file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def find_max_difference_graph(graph6_list):
    """
    Given a list of graph6 strings, return:
        - the graph6 string with the largest max-degree-difference
        - the corresponding NetworkX graph
        - the max difference value
    """
    best_g6 = []
    best_graph = []
    best_diff = -1

    for g6 in graph6_list:
        G = nx.from_graph6_bytes(g6.encode())
        diff = max_degree_difference(G)

        if diff == best_diff:
            best_g6.append(g6)
            best_graph.append(G)
        if diff > best_diff:
            best_diff = diff
            best_g6 = [g6]
            best_graph = [G]

    return best_g6, best_graph, best_diff


if __name__ == "__main__":
    # Load graphs from file
    graphs = load_graphs('graphs.txt')
    
    # Find the graph with maximum degree difference
    best_g6, best_graph, diff = find_max_difference_graph(graphs)
    
    print("Number of best graphs found:", len(best_g6))
    print("Best graph6:", best_g6[0])
    print("Max degree difference:", diff)

    if diff > 1:
        print("Degree difference is greater than 1, so the conjecture is false.")
    
    # Visualize the best graph
    visualize_difference(best_graph[0])
    visualize_graph6_diff(best_g6[0])
