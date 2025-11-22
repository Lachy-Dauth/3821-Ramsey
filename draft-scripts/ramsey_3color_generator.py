#!/usr/bin/env python3
"""
3-Color Ramsey Number Lower Bound Generator - CYCLIC COLORINGS

Uses cyclic (circulant) colorings where edge color depends only on distance.
For vertices labeled 0,...,N-1, edge (a,b) has color C(|a-b|) where distance
is taken cyclically: dist(a,b) = min(|a-b|, N-|a-b|).

This dramatically reduces search space from 3^N to 3^(N/2) due to symmetry.
"""

import numpy as np
import matplotlib.pyplot as plt
import itertools
import json
import os
from datetime import datetime
from typing import List, Tuple, Set, Dict


def rough_value3(a, b, c):
    """
    Symmetric rough fit (minimised percentage error for small values).
    Returns an estimate of R(a,b,c) to use for optimization.
    """
    A = 6.54051472471042
    B = -7.384396766909559
    C = 2.3153635733893423
    D = 23.368642703367474
    s1 = a + b + c
    s2 = a*b + b*c + c*a
    s3 = a*b*c
    return s1 - s3 / 100


def optimization_score(ramsey_vals, target):
    """
    Score function to minimize. Lower is better.
    Uses the rough estimate function.
    """
    a, b, c = ramsey_vals
    return rough_value3(a, b, c)


class CyclicColoring:
    """
    Represents a cyclic (distance-based) coloring pattern.
    For N vertices, we only need to specify colors for distances 1, 2, ..., floor(N/2).
    Due to cyclic symmetry, distance d from the "other direction" gets the same color.
    """
    
    def __init__(self, n_vertices: int, distance_colors: List[int] = None):
        """
        Initialize cyclic coloring.
        n_vertices: number of vertices in the graph
        distance_colors: list of colors for distances 1, 2, ..., floor(n/2)
        """
        self.n = n_vertices
        self.max_distance = n_vertices // 2
        
        if distance_colors is None:
            # Default: all distances get color 0
            self.distance_colors = [0] * self.max_distance
        else:
            assert len(distance_colors) == self.max_distance, \
                f"Need {self.max_distance} distance colors for {n_vertices} vertices"
            self.distance_colors = list(distance_colors)
    
    def get_color(self, v1: int, v2: int) -> int:
        """Get the color of edge between vertices v1 and v2."""
        if v1 == v2:
            return -1  # No self-loops
        
        # Compute cyclic distance
        diff = abs(v1 - v2)
        distance = min(diff, self.n - diff)
        
        # Distance is 1-indexed in our array (distance 1 is at index 0)
        return self.distance_colors[distance - 1]
    
    def to_adjacency_matrix(self) -> np.ndarray:
        """Convert to full adjacency matrix."""
        edges = np.full((self.n, self.n), -1, dtype=np.int8)
        for i in range(self.n):
            for j in range(i + 1, self.n):
                color = self.get_color(i, j)
                edges[i][j] = color
                edges[j][i] = color
        return edges
    
    def __repr__(self):
        return f"CyclicColoring(n={self.n}, distances={self.distance_colors})"


class RamseyGraph:
    """
    Represents a 3-edge-colored complete graph using cyclic coloring.
    Colors: 0 (red), 1 (blue), 2 (green)
    """
    
    def __init__(self, coloring: CyclicColoring):
        """Initialize with a cyclic coloring."""
        self.coloring = coloring
        self.n = coloring.n
        self.edges = coloring.to_adjacency_matrix()
    
    @classmethod
    def from_vertices(cls, n_vertices: int, distance_colors: List[int] = None):
        """Create a graph from number of vertices and distance coloring."""
        coloring = CyclicColoring(n_vertices, distance_colors)
        return cls(coloring)
    
    def check_monochromatic_clique(self, vertices: List[int], color: int) -> bool:
        """Check if given vertices form a monochromatic clique in the specified color."""
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                v1, v2 = vertices[i], vertices[j]
                if self.edges[v1][v2] != color:
                    return False
        return True
    
    def find_ramsey_values(self) -> Tuple[int, int, int]:
        """
        Find the maximum sizes of monochromatic cliques for each color.
        Returns (max_red, max_blue, max_green)
        Optimized: stop searching once we find a clique of certain size.
        """
        max_sizes = [0, 0, 0]
        
        # Check all possible subsets of vertices, starting from larger sizes
        # This allows early termination when we find large cliques
        for size in range(self.n, 0, -1):
            found_new = False
            for subset in itertools.combinations(range(self.n), size):
                for color in range(3):
                    if max_sizes[color] < size:  # Only check if we haven't found this size yet
                        if self.check_monochromatic_clique(list(subset), color):
                            max_sizes[color] = max(max_sizes[color], size)
                            found_new = True
            # If we've found max cliques of this size for all colors, we can stop
            if not found_new and min(max_sizes) >= size - 1:
                break
        
        return tuple(max_sizes)
    
    def to_dict(self) -> dict:
        """Convert graph to dictionary for JSON serialization."""
        return {
            'n_vertices': self.n,
            'distance_colors': self.coloring.distance_colors,
            'edges': self.edges.tolist()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RamseyGraph':
        """Create graph from dictionary."""
        coloring = CyclicColoring(data['n_vertices'], data['distance_colors'])
        return cls(coloring)


def generate_all_cyclic_colorings(n: int, prev_colors: List[int] = None) -> List[List[int]]:
    """
    Generate all possible cyclic colorings for n vertices.
    
    For n vertices, we need to specify colors for distances 1, 2, ..., floor(n/2).
    
    If prev_colors is provided (from n-1 vertices), we extend it efficiently:
    - Keep the first len(prev_colors) distance colors
    - Add one new distance color (only if n is even, we get a new distance n/2)
    
    Returns: list of distance color patterns
    """
    max_distance = n // 2
    
    if prev_colors is None:
        # Generate all possible colorings from scratch
        return list(itertools.product([0, 1, 2], repeat=max_distance))
    
    # Extending from previous: check if we need a new distance
    prev_max_distance = (n - 1) // 2
    
    if max_distance == prev_max_distance:
        # Same number of distances, just increment vertex count
        # The coloring stays exactly the same!
        return [prev_colors]
    else:
        # New distance appears (when going from odd to even n)
        # Try all 3 colors for the new middle distance
        results = []
        for new_color in [0, 1, 2]:
            results.append(prev_colors + [new_color])
        return results


def visualize_graph(graph: RamseyGraph, ramsey_vals: Tuple[int, int, int], 
                   filename: str, iteration: int):
    """
    Visualize the 3-colored graph using matplotlib.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    n = graph.n
    # Arrange vertices in a circle
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)
    
    # Color mapping
    color_names = ['red', 'blue', 'green']
    edge_colors = ['#FF6B6B', '#4ECDC4', '#95E77D']
    
    # Draw edges
    for i in range(n):
        for j in range(i + 1, n):
            color = graph.edges[i][j]
            if color >= 0:
                ax.plot([x[i], x[j]], [y[i], y[j]], 
                       color=edge_colors[color], alpha=0.6, linewidth=1.5)
    
    # Draw vertices
    ax.scatter(x, y, s=500, c='white', edgecolors='black', linewidths=2, zorder=10)
    
    # Label vertices
    for i in range(n):
        ax.text(x[i], y[i], str(i), ha='center', va='center', 
               fontsize=12, fontweight='bold', zorder=11)
    
    # Title with Ramsey values
    a, b, c = ramsey_vals
    title = f'3-Color Cyclic Ramsey Graph: {n} vertices (Iteration {iteration})\n'
    title += f'Max Cliques: Red={a}, Blue={b}, Green={c}\n'
    if hasattr(graph, 'coloring'):
        title += f'Distance colors: {graph.coloring.distance_colors}'
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved visualization: {filename}")


def generate_all_colorings(n: int) -> List[List[int]]:
    """
    Generate all possible 3-colorings for n edges.
    Returns list of colorings, each is a list of n colors (0, 1, or 2).
    """
    return list(itertools.product([0, 1, 2], repeat=n))


def main():
    """Main generation loop using cyclic colorings."""
    print("=" * 70)
    print("3-COLOR RAMSEY NUMBER LOWER BOUND GENERATOR")
    print("Using CYCLIC (CIRCULANT) COLORINGS")
    print("=" * 70)
    print()
    
    # Create output directory
    output_dir = "ramsey_3color_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Target Ramsey values to optimize for
    target = [3, 3, 3]
    print(f"🎯 Optimization strategy: Minimize rough_value3(a,b,c)")
    print(f"🔄 Using cyclic colorings: edge color depends only on distance")
    print()
    
    # Initialize with 3 vertices (minimum for interesting cyclic graph)
    # Start with a better initial configuration - try to mix colors
    # Let's start with distance 1 having different colors to explore
    print("🔍 Finding best initial 3-vertex configuration...")
    best_init = None
    best_init_score = float('inf')
    
    for color in [0, 1, 2]:
        test_graph = RamseyGraph.from_vertices(3, [color])
        test_ramsey = test_graph.find_ramsey_values()
        test_score = optimization_score(test_ramsey, target)
        print(f"   Distance [color {color}]: R{test_ramsey}, score={test_score:.2f}")
        if test_score < best_init_score:
            best_init_score = test_score
            best_init = (test_graph, test_ramsey, [color])
    
    current_graph, current_ramsey, current_distance_colors = best_init
    
    # History of best graphs
    history = []
    
    iteration = 0
    max_vertices = 50  # Can go much higher with cyclic colorings!
    
    print(f"Starting with {current_graph.n} vertices")
    print(f"Initial distance coloring: {current_distance_colors}")
    print(f"Initial Ramsey values: R{current_ramsey}")
    print(f"Will stop at {max_vertices} vertices")
    print()
    
    import time
    start_time = time.time()
    
    while current_graph.n < max_vertices:
        iteration += 1
        n = current_graph.n
        next_n = n + 1
        
        print(f"{'='*70}")
        print(f"ITERATION {iteration}: Growing from {n} to {next_n} vertices")
        print(f"{'='*70}")
        
        # Generate all possible cyclic colorings for next size
        all_distance_colorings = generate_all_cyclic_colorings(next_n, current_distance_colors)
        iter_start = time.time()
        
        num_colorings = len(all_distance_colorings)
        print(f"  Current distance coloring: {current_distance_colors}")
        print(f"  Testing {num_colorings} cyclic coloring(s)")
        
        if num_colorings == 1:
            print(f"  ℹ️  Only 1 coloring (odd→even transition, no new distance)")
        else:
            print(f"  ℹ️  New middle distance appears, trying all 3 colors")
        
        # Evaluate all candidates
        candidates = []
        found_matching = False
        
        for idx, distance_coloring in enumerate(all_distance_colorings):
            new_graph = RamseyGraph.from_vertices(next_n, distance_coloring)
            ramsey_vals = new_graph.find_ramsey_values()
            
            # Check if this matches the previous best - if so, take it immediately!
            if ramsey_vals == current_ramsey:
                print(f"  ⚡ EARLY MATCH FOUND!")
                print(f"     Ramsey values maintained: R{ramsey_vals}")
                print(f"     Distance coloring: {distance_coloring}")
                print(f"     Taking this immediately (no point searching further).")
                score = optimization_score(ramsey_vals, target)
                best_graph = new_graph
                best_ramsey = ramsey_vals
                best_score = score
                best_distance_coloring = distance_coloring
                found_matching = True
                break
            
            score = optimization_score(ramsey_vals, target)
            candidates.append((new_graph, ramsey_vals, score, distance_coloring))
        
        # If we didn't find an early match, select best
        if not found_matching:
            if not candidates:
                print("  ❌ No valid candidates found!")
                break
            
            # Sort by score (lower is better)
            candidates.sort(key=lambda x: x[2])
            best_graph, best_ramsey, best_score, best_distance_coloring = candidates[0]
            
            print(f"  ✓ Best configuration found:")
            print(f"    Ramsey values: R{best_ramsey}")
            print(f"    Optimization score: {best_score:.2f}")
            print(f"    Distance coloring: {best_distance_coloring}")
        
        # Check if this is a new optimal configuration (Ramsey values changed)
        is_new_optimal = (best_ramsey != current_ramsey)
        
        if is_new_optimal or iteration % 5 == 1:  # Save at interesting points
            # Save visualization
            filename = os.path.join(output_dir, 
                                   f"ramsey_n{best_graph.n}_R{best_ramsey}_iter{iteration}.png")
            visualize_graph(best_graph, best_ramsey, filename, iteration)
            
            # Save graph data
            graph_data = {
                'iteration': iteration,
                'n_vertices': best_graph.n,
                'ramsey_values': best_ramsey,
                'distance_coloring': best_distance_coloring,
                'optimization_score': best_score,
                'graph': best_graph.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            json_filename = os.path.join(output_dir, 
                                        f"ramsey_n{best_graph.n}_R{best_ramsey}_iter{iteration}.json")
            with open(json_filename, 'w') as f:
                json.dump(graph_data, f, indent=2)
            print(f"  💾 Saved graph data: {json_filename}")
        
        # Update current graph
        history.append({
            'iteration': iteration,
            'n_vertices': best_graph.n,
            'ramsey_values': best_ramsey,
            'distance_coloring': best_distance_coloring,
            'score': best_score
        })
        current_graph = best_graph
        current_ramsey = best_ramsey
        current_distance_colors = best_distance_coloring
        
        print()
    
    # Save complete history
    history_file = os.path.join(output_dir, "generation_history.json")
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print()
    elapsed_time = time.time() - start_time
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print()
    print("📊 Summary of progression:")
    print("-" * 70)
    print("Iter\tVertices\tDistance Coloring\t\tRamsey Values\tScore")
    print("-" * 70)
    for entry in history:
        it = entry['iteration']
        n = entry['n_vertices']
        dc = entry['distance_coloring']
        rv = entry['ramsey_values']
        sc = entry['score']
        # Shorten distance coloring display if too long
        dc_str = str(dc) if len(dc) <= 10 else str(dc[:10]) + "..."
        print(f"{it}\t{n}\t\t{dc_str:20s}\tR{rv}\t{sc:.2f}")
    
    print()
    print(f"📈 Final graph: {current_graph.n} vertices")
    print(f"🎨 Final distance coloring: {current_distance_colors}")
    print(f"📊 Final Ramsey values: R{current_ramsey}")
    print()
    print("✨ Interpretation:")
    a, b, c = current_ramsey
    print(f"  This cyclic graph shows that R({a}, {b}, {c}) > {current_graph.n}")
    print(f"  Meaning: There exists a 3-coloring of K_{current_graph.n} that avoids:")
    print(f"    - A red K_{a}")
    print(f"    - A blue K_{b}")
    print(f"    - A green K_{c}")
    print()
    print(f"🔄 The coloring is CYCLIC (circulant):")
    print(f"   Edge between vertices at distance d has color: {dict(enumerate(current_distance_colors, 1))}")
    print()
    print(f"📁 All outputs saved to: {output_dir}/")


if __name__ == "__main__":
    main()
