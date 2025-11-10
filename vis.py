import networkx as nx
import matplotlib.pyplot as plt

# Function to visualize graph6 graphs
def visualize_graph6(graph6_str):
    # Parse the graph6 string into a NetworkX graph
    G = nx.from_graph6_bytes(graph6_str.encode())

    # Use spring layout (force-directed)
    pos = nx.spring_layout(G, seed=42, k=None, iterations=100)

    # Draw the graph with labels and nice styling
    plt.figure(figsize=(6, 6))
    nx.draw(
        G,
        pos,
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

# Example usage:
# visualize_graph6('Dhc')
visualize_graph6('Ls`?XGRQR@B`Kc')
visualize_graph6('W?CX@DDWc[PJUtlYnHDtAdeIhSYZDYn`iQeY[NWNKON|ef?')
