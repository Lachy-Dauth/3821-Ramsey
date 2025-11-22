# 3821-Ramsey

The repository contains code for the CS3821 assignment on Ramsey theory. 

## conjecture-1.py
This script tests Conjecture 1, and specifically disproves it via counterexample. The `subgraphs.txt` and `supergraphs.txt` files contain extremal R(3,5) and R(4,5) respectively in graph6 format, from an [ANU dataset](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html). The script checks all combinations of subgraphs for each supergraph and looks for a subgraph isomorphism. If none exists then the conjecture is false, which is the case.

## conjecture-2.py
This script tests Conjecture 2 by analyzing the maximum degree difference across all pairs of vertices in extremal Ramsey graphs. The script loads graph6 strings from `graphs.txt` and finds the graph(s) with the largest maximum degree difference. It uses visualization helper functions from `vis.py` to display the results. If the maximum degree difference is greater than 1, the conjecture is disproved, which is the case.

## vis.py
A helper library providing graph visualization and analysis utilities for working with graph6 formatted graphs. Key functions include:
- `visualize_graph6()`: Basic visualization of a graph6 string using a spring layout
- `visualize_graph6_diff()`: Highlights the two nodes with maximum degree difference
- `visualize_difference()`: Custom layout emphasizing degree differences with highlighted nodes at the top

## Draft scripts
Draft scripts contains draft code that was created to attempt to generate Cyclic 3 color ramsey based on the paper [Computational lower limits on small Ramsey numbers](https://arxiv.org/abs/1505.07186) by Eugene Kuznetsov. I only started work on this approach late in the assignment period after the other methods had failed, so the code is incomplete and unpolished. However, I strongly believe it has significant merit for future work.