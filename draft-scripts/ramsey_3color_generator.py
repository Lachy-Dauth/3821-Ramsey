#!/usr/bin/env python3
"""
3-Color Ramsey Number Lower Bound Generator - KUZNETSOV'S ALGORITHM

Implements the Cyclic Coloring Search algorithm from:
"Computational lower limits on small Ramsey numbers" by Eugene Kuznetsov (2015).

Methodology:
1. Represents graphs as cyclic colorings (determined by distance).
2. Uses operations (Relabel, Reflection, Bit Flip) to explore the space.
3. Maintains a pool of valid graphs and tries to grow them.
"""

import numpy as np
import networkx as nx
import itertools
import os
import random
import math
import argparse
import sys
from datetime import datetime
from typing import List, Tuple, Set

# Configuration
# Target clique sizes to AVOID.
# We are looking for graphs that do NOT have cliques of these sizes.
# Example: [3, 3, 4] means we want graphs with:
# - No Red K3
# - No Blue K3
# - No Green K4
TARGET_CLIQUES = [3, 5, 5] 

class CyclicColoring:
    """Represents a cyclic (distance-based) coloring pattern."""
    
    def __init__(self, n_vertices: int, distance_colors: List[int] = None):
        self.n = n_vertices
        self.max_distance = n_vertices // 2
        
        if distance_colors is None:
            self.distance_colors = [0] * self.max_distance
        else:
            if len(distance_colors) > self.max_distance:
                self.distance_colors = list(distance_colors[:self.max_distance])
            elif len(distance_colors) < self.max_distance:
                self.distance_colors = list(distance_colors) + [0] * (self.max_distance - len(distance_colors))
            else:
                self.distance_colors = list(distance_colors)
    
    def get_color(self, v1: int, v2: int) -> int:
        if v1 == v2: return -1
        diff = abs(v1 - v2)
        distance = min(diff, self.n - diff)
        return self.distance_colors[distance - 1]
    
    def get_row(self) -> List[int]:
        """Get the first row of the adjacency matrix (excluding diagonal)."""
        row = []
        for i in range(1, self.n):
            dist = min(i, self.n - i)
            row.append(self.distance_colors[dist - 1])
        return row

    @classmethod
    def from_row(cls, row: List[int]) -> 'CyclicColoring':
        """Create from row representation."""
        n = len(row) + 1
        max_dist = n // 2
        distances = []
        for d in range(1, max_dist + 1):
            distances.append(row[d-1])
        return cls(n, distances)

    def to_adjacency_matrix(self) -> np.ndarray:
        edges = np.full((self.n, self.n), -1, dtype=np.int8)
        for i in range(self.n):
            for j in range(i + 1, self.n):
                color = self.get_color(i, j)
                edges[i][j] = color
                edges[j][i] = color
        return edges
    
    def __repr__(self):
        return f"CyclicColoring(n={self.n}, dists={self.distance_colors})"
    
    def __eq__(self, other):
        return self.n == other.n and self.distance_colors == other.distance_colors
    
    def __hash__(self):
        return hash((self.n, tuple(self.distance_colors)))


class RamseyGraph:
    """Represents a 3-edge-colored complete graph using cyclic coloring."""
    
    def __init__(self, coloring: CyclicColoring):
        self.coloring = coloring
        self.n = coloring.n
        self.edges = coloring.to_adjacency_matrix()
        self._max_cliques = None
    
    def check_clique_size_limit(self, limits: List[int]) -> bool:
        """Check if the graph respects the clique size limits."""
        for color, limit in enumerate(limits):
            if self._has_clique_of_size(limit, color):
                return False
        return True

    def _has_clique_of_size(self, k: int, color: int) -> bool:
        """Check if there exists a clique of size k in specific color."""
        if k <= 1: return True
        if k > self.n: return False
        
        candidates = [v for v in range(1, self.n) if self.edges[0][v] == color]
        
        if len(candidates) < k - 1:
            return False
            
        for subset in itertools.combinations(candidates, k - 1):
            if self._is_clique(subset, color):
                return True
        return False

    def _is_clique(self, vertices: List[int], color: int) -> bool:
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                if self.edges[vertices[i]][vertices[j]] != color:
                    return False
        return True

    def find_ramsey_values(self) -> Tuple[int, int, int]:
        """Find max clique sizes."""
        if self._max_cliques: return self._max_cliques
        
        max_sizes = [0, 0, 0]
        for color in range(3):
            for size in range(min(self.n, TARGET_CLIQUES[color] + 2), 0, -1):
                if self._has_clique_of_size(size, color):
                    max_sizes[color] = size
                    break
        
        self._max_cliques = tuple(max_sizes)
        return self._max_cliques

    def to_dict(self) -> dict:
        return {
            'n_vertices': self.n,
            'distance_colors': self.coloring.distance_colors,
            'ramsey_values': self.find_ramsey_values()
        }

    def to_graph6(self) -> dict:
        """
        Convert to graph6 format string using NetworkX.
        Returns a dictionary with graph6 strings for each color channel.
        """
        results = {}
        colors = ['red', 'blue', 'green']
        
        for c_idx, color_name in enumerate(colors):
            # Create NetworkX graph for this color
            G = nx.Graph()
            G.add_nodes_from(range(self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    if self.edges[i][j] == c_idx:
                        G.add_edge(i, j)
            
            # Convert to graph6
            # header=False avoids the ">>graph6<<" prefix if supported
            try:
                g6_bytes = nx.to_graph6_bytes(G, header=False)
            except TypeError:
                # Fallback for older networkx versions that might not have header arg
                g6_bytes = nx.to_graph6_bytes(G)
                if g6_bytes.startswith(b">>graph6<<"):
                    g6_bytes = g6_bytes[10:]
            
            g6_str = g6_bytes.decode('ascii').strip()
            results[color_name] = g6_str
            
        return results



class CyclicOperations:
    """Implements Kuznetsov's operations on cyclic colorings."""
    
    @staticmethod
    def relabel(coloring: CyclicColoring, M: int) -> CyclicColoring:
        """Relabel vertices: b'(x) = b((M(x+1) mod N) - 1)."""
        N = coloring.n
        if math.gcd(M, N) != 1:
            return None
            
        old_row = coloring.get_row()
        new_row = [0] * (N - 1)
        
        for x in range(N - 1):
            target_idx = (M * (x + 1)) % N - 1
            new_row[x] = old_row[target_idx]
            
        return CyclicColoring.from_row(new_row)

    @staticmethod
    def reflection(coloring: CyclicColoring, target_n: int) -> CyclicColoring:
        """Reflection operation to resize graph."""
        old_row = coloring.get_row()
        L_new = target_n - 1
        
        prefix_len = math.ceil(L_new / 2)
        suffix_len = math.floor(L_new / 2)
        
        def get_bit(idx, row):
            if 0 <= idx < len(row): return row[idx]
            return 0
            
        new_row = []
        for i in range(prefix_len):
            new_row.append(get_bit(i, old_row))
            
        for i in range(suffix_len):
            idx = len(old_row) - suffix_len + i
            new_row.append(get_bit(idx, old_row))
            
        return CyclicColoring.from_row(new_row)

    @staticmethod
    def bit_flip(coloring: CyclicColoring, distance_idx: int, new_color: int) -> CyclicColoring:
        """Change color of a specific distance."""
        dists = list(coloring.distance_colors)
        if 0 <= distance_idx < len(dists):
            dists[distance_idx] = new_color
        return CyclicColoring(coloring.n, dists)


class KuznetsovSearch:
    """Implements the search strategy."""
    def __init__(self, target_cliques: List[int]):
        self.target = target_cliques
        self.pool = set()
        self.best_graph = None
        self.l_min = 0
        
    def initialize(self):
        """Start with small valid graphs."""
        print(f"Initializing search for graphs avoiding cliques {self.target}...")
        for _ in range(20):
            dists = [random.choice([0, 1, 2]) for _ in range(2)]
            c = CyclicColoring(5, dists)
            g = RamseyGraph(c)
            if g.check_clique_size_limit(self.target):
                self.pool.add(c)
                self._update_best(g)
        
        if not self.pool:
            self.pool.add(CyclicColoring(3, [0]))
            
        print(f"  Initial pool size: {len(self.pool)}")
        self.l_min = max(c.n for c in self.pool)

    def _update_best(self, graph: RamseyGraph):
        if self.best_graph is None or graph.n > self.best_graph.n:
            self.best_graph = graph
            print(f"  New best size: {graph.n} vertices! (R values: {graph.find_ramsey_values()})")
            self.l_min = max(self.l_min, graph.n - 5)

    def step(self):
        """Perform one iteration of the search algorithm."""
        new_candidates = set()
        
        sorted_pool = sorted(list(self.pool), key=lambda c: c.n, reverse=True)
        sorted_pool = sorted_pool[:100] 
        
        for coloring in sorted_pool:
            # A. Relabeling
            coprimes = [m for m in range(1, coloring.n) if math.gcd(m, coloring.n) == 1]
            selected_ms = random.sample(coprimes, min(len(coprimes), 5))
            
            relabeled_forms = []
            for M in selected_ms:
                r = CyclicOperations.relabel(coloring, M)
                if r: relabeled_forms.append(r)
            relabeled_forms.append(coloring)
            
            # B. Reflection (Grow) & Bit Flips
            for base_c in relabeled_forms:
                for grow in [1]:
                    target_n = base_c.n + grow
                    reflected = CyclicOperations.reflection(base_c, target_n)
                    
                    self._check_and_add(reflected, new_candidates)
                    
                    num_dists = len(reflected.distance_colors)
                    indices = range(num_dists)
                    if num_dists > 10:
                        indices = random.sample(range(num_dists), 10)
                        
                    for idx in indices:
                        current_color = reflected.distance_colors[idx]
                        for c in [0, 1, 2]:
                            if c != current_color:
                                flipped = CyclicOperations.bit_flip(reflected, idx, c)
                                self._check_and_add(flipped, new_candidates)
                                
                    # Bit Swap
                    if num_dists >= 2:
                        for _ in range(5):
                            idx1, idx2 = random.sample(range(num_dists), 2)
                            c1 = reflected.distance_colors[idx1]
                            c2 = reflected.distance_colors[idx2]
                            if c1 != c2:
                                swapped = CyclicOperations.bit_flip(reflected, idx1, c2)
                                swapped = CyclicOperations.bit_flip(swapped, idx2, c1)
                                self._check_and_add(swapped, new_candidates)

        self.pool = {c for c in new_candidates if c.n >= self.l_min}
        
        if len(self.pool) < 10:
            if self.best_graph:
                self.pool.add(self.best_graph.coloring)
                
        print(f"  Pool size: {len(self.pool)} (l_min={self.l_min})")

    def _check_and_add(self, coloring: CyclicColoring, candidate_set: Set[CyclicColoring]):
        g = RamseyGraph(coloring)
        if g.check_clique_size_limit(self.target):
            candidate_set.add(coloring)
            self._update_best(g)







def main():
    global TARGET_CLIQUES
    
    parser = argparse.ArgumentParser(description="3-Color Ramsey Number Lower Bound Generator")
    parser.add_argument("--target", type=int, nargs=3, default=[3, 5, 5], help="Target clique sizes (e.g. 3 5 5)")
    parser.add_argument("--iterations", type=int, default=200, help="Maximum iterations")
    args = parser.parse_args()
    
    TARGET_CLIQUES = args.target
    max_iterations = args.iterations

    print("=" * 70)
    print("KUZNETSOV'S CYCLIC COLORING SEARCH")
    print(f"Targeting graphs avoiding cliques: {TARGET_CLIQUES}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)
    
    search = KuznetsovSearch(TARGET_CLIQUES)
    search.initialize()
    
    start_time = datetime.now()
    
    for i in range(max_iterations):
        print(f"\nIteration {i+1}/{max_iterations}")
        search.step()
                
    print("\nSearch Complete.")
    if search.best_graph:
        print(f"Best graph found: N={search.best_graph.n}")
        print(f"Distance coloring: {search.best_graph.coloring.distance_colors}")
        print(f"Ramsey values: {search.best_graph.find_ramsey_values()}")
        g6 = search.best_graph.to_graph6()
        print(f"Graph6 (Red): {g6['red']}")
        print(f"Graph6 (Blue): {g6['blue']}")
        print(f"Graph6 (Green): {g6['green']}")
        
        # Validation using vis.py
        try:
            # Add parent directory to path to import vis
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            import vis
            
            print("\nValidating with vis.py helper...")
            colors = ['red', 'blue', 'green']
            all_valid = True
            
            for i, color in enumerate(colors):
                g6_str = g6[color]
                # Create NX graph from graph6 string
                # Note: graph6 string might need encoding if it's a string
                try:
                    G_nx = nx.from_graph6_bytes(g6_str.encode('ascii'))
                except:
                    G_nx = nx.from_graph6_bytes(g6_str)
                    
                # validate_ramsey_helper returns True if max clique < target
                is_valid = vis.validate_ramsey_helper(G_nx, TARGET_CLIQUES[i])
                
                status = "PASS" if is_valid else "FAIL"
                print(f"  Color {color} (Target < {TARGET_CLIQUES[i]}): {status}")
                
                if not is_valid:
                    all_valid = False
                    # Double check actual clique size
                    clique = nx.max_weight_clique(G_nx, weight=None)[0]
                    print(f"    -> Found clique of size {len(clique)}")

            if all_valid:
                print("VALIDATION SUCCESSFUL: Graph satisfies all Ramsey constraints.")
            else:
                print("VALIDATION FAILED: Graph contains forbidden cliques.")
                
        except ImportError:
            print("\nCould not import vis.py for validation (not found in parent directory).")
        except Exception as e:
            print(f"\nValidation error: {e}")

    else:
        print("No valid graphs found.")

if __name__ == "__main__":
    main()
