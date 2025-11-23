import networkx as nx
import matplotlib.pyplot as plt
import math

def visualize_graph6(graph6_str):
    G = nx.from_graph6_bytes(graph6_str.encode())
    pos = nx.spring_layout(G, seed=42, iterations=100)

    plt.figure(figsize=(6,6))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color='skyblue',
        node_size=500,
        font_size=10,
        font_weight='bold',
        edge_color='gray'
    )
    plt.title("Graph6 Visualisation")
    plt.axis('off')
    plt.show()
    return G

def visualize_graph6_diff(graph6_str):
    # visualize graph 6 with the two nodes of max degree difference in different colors using a spring layout
    G = nx.from_graph6_bytes(graph6_str.encode())

    degrees = dict(G.degree())
    nodes = list(G.nodes())

    # Find the pair with the largest degree difference
    max_pair = None
    max_diff = -1
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            diff = abs(degrees[nodes[i]] - degrees[nodes[j]])
            if diff > max_diff:
                max_diff = diff
                max_pair = (nodes[i], nodes[j])

    a, b = max_pair

    # Spring layout
    pos = nx.spring_layout(G, seed=42, iterations=100)

    # Color mapping: highlight a and b
    node_colors = []
    for n in G.nodes():
        if n == a:
            node_colors.append('lightgreen')
        elif n == b:
            node_colors.append('lightgreen')
        else:
            node_colors.append('skyblue')

    plt.figure(figsize=(6, 3))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=500,
        font_size=10,
        font_weight='bold',
        edge_color='gray'
    )
    plt.title("Graph6 with Max Degree-Difference Nodes Highlighted")
    plt.axis('off')
    plt.show()

    return G, (a, b), max_diff


def visualize_difference(G):
    degrees = dict(G.degree())

    # Find the pair with the largest degree difference
    nodes = list(G.nodes())
    max_pair = None
    max_diff = -1

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            diff = abs(degrees[nodes[i]] - degrees[nodes[j]])
            if diff > max_diff:
                max_diff = diff
                max_pair = (nodes[i], nodes[j])

    a, b = max_pair

    # Create custom layout
    pos = {}

    # Top positions for the two distinguished nodes
    pos[a] = (-0.4, 0)
    pos[b] = (0.4, 0)

    # Remaining nodes arranged in an oval
    remaining = [n for n in nodes if n not in (a, b)]
    k = len(remaining)

    for i, n in enumerate(remaining):
        angle = -0.9 * math.pi * i / k - 0.05 * math.pi
        x = 0.8 * math.cos(angle)
        y = -0.2 + 0.35 * math.sin(angle)  # slight oval below
        pos[n] = (x, y)

    # Draw
    plt.figure(figsize=(7,3))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color='lightgreen',
        node_size=500,
        font_size=10,
        font_weight='bold',
        edge_color='gray'
    )
    plt.title("Degree-Difference Layout")
    plt.axis('off')
    plt.show()

def max_degree_difference(G):
    """Return max |deg(u) - deg(v)| over all node pairs."""
    deg = dict(G.degree())
    nodes = list(G.nodes())

    max_diff = 0
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            diff = abs(deg[nodes[i]] - deg[nodes[j]])
            if diff > max_diff:
                max_diff = diff
    return max_diff

def validate_ramsey_helper(G, n):
    max_clique_nodes = nx.max_weight_clique(G, weight=None)[0]
    clique_size = len(max_clique_nodes)
    
    if clique_size >= n:
        return False

    return True

if __name__ == "__main__":
    g6 = "~?@pUWooWE?sBWEWEkBJ?tWEt_Xj?tj?ut_ZlWE|j?vukB^lWE~lWE~ukBN|j?t~lWEv}t_Zn|j?vn|j?rv}t_W|~lWEFn|j?o]~ukB?|~lWE?|~lWE_]~ukBGFn|j?p?|~lWECBv}t_WGFn|j?oGFn|j?oCBv}t_W@?|~lWE?GFn|j?o?_]~ukB?@?|~lWE?@?|~lWE??_]~ukB??GFn|j?s?@?|~lWEO?CBv}t_W_?GFn|j?o_?GFn|j?oO?CBv}t_WC?@?|~lWE?_?GFn|j?oA??_]~ukB?C?@?|~lWE?C?@?|~lWE?A??_]~ukBO?_?GFn|j?q?C?@?|~lWEG?O?CBv}t_WO?_?GFn|j?oO?_?GFn|j?oG?O?CBv}t_WA?C?@?|~lWE?O?_?GFn|j?o@?A??_]~ukB?A?C?@?|~lWE?A?C?@?|~lWE?@?A??_]~ukB??O?_?GFn|j?o?A?C?@?|~lWE_?G?O?CBv}t_X??O?_?GFn|j?p??O?_?GFn|j?o_?G?O?CBv}t_WG?A?C?@?|~lWE@??O?_?GFn|j?oC?@?A??_]~ukBOG?A?C?@?|~lWEoG?A?C?@?|~lWEwC?@?A??_]~ukB]@??O?_?GFn|j?roG?A?C?@?|~lWEn?_?G?O?CBv}t_Z]@??O?_?GFn|j?v]@??O?_?GFn|j?vn?_?G?O?CBv}t_ZzoG?A?C?@?|~lWE~]@??O?_?GFn|j?v|wC?@?A??_]~ukB^zoG?A?C?@?|~lWE^zoG?A?C?@?|~lWEn|wC?@?A??_]~ukBZ~]@??O?_?GFn|j?r^zoG?A?C?@?|~lWEl~n?_?G?O?CBv}t_XZ~]@??O?_?GFn|j?tZ~]@??O?_?GFn|j?ul~n?_?G?O?CBv}t_Xj^zoG?A?C?@?|~lWELZ~]@??O?_?GFn|j?otn|wC?@?A??_]~ukB@j^zoG?A?C?@?|~lWE@j^zoG?A?C?@?|~lWE?tn|wC?@?A??_]~ukBOLZ~]@??O?_?GFn|j?u@j^zoG?A?C?@?|~lWEWEl~n?_?G?O?CBv}t_W"
    G = visualize_graph6(g6)
    diff = max_degree_difference(G)
    print("Max degree difference:", diff)
    print(validate_ramsey_helper(G, 3))