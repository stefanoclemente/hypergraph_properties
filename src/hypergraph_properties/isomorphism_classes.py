import itertools
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from hypergraph_properties.hypergraph import *
def _popcount(x):
    """
    Return the number of 1-bits in the integer x (population count).

    We prefer int.bit_count() when available (Python 3.8+), but keep
    a safe fallback for older interpreters.
    """
    try:
        return x.bit_count()
    except AttributeError:
        return bin(x).count("1")


def _mask_to_frozenset(mask, n):
    """
    Convert an n-bit mask into a frozenset of vertex labels in {1,...,n}.

    Bit i (0-based) corresponds to vertex (i+1).
    """
    out = []
    for i in range(n):
        if (mask >> i) & 1:
            out.append(i + 1)
    return frozenset(out)


def _incidence_graph_from_masks(edge_masks, n):
    """
    Build the bipartite incidence graph B(H) for an hypergraph H described by:
      - n vertices labeled 1..n
      - hyperedges given as bitmasks in edge_masks

    Node encoding:
      - vertex-side nodes are ("v", v) with attribute bipartite=0
      - edge-side nodes are ("e", eid) with attributes:
          bipartite=1
          size = |hyperedge|

    Edges:
      - connect ("e", eid) to ("v", v) iff v is contained in hyperedge eid.
    """
    B = nx.Graph()

    # Add vertex-side nodes.
    for v in range(1, n + 1):
        B.add_node(("v", v), bipartite=0)

    # Add edge-side nodes + incidence edges.
    for eid, m in enumerate(edge_masks):
        enode = ("e", eid)
        sz = _popcount(m)
        B.add_node(enode, bipartite=1, size=sz)

        # For every vertex present in the bitmask, add incidence edge.
        for i in range(n):
            if (m >> i) & 1:
                B.add_edge(enode, ("v", i + 1))

    return B


def _node_match(a, b):
    """
    Exact node-matching rule for GraphMatcher on incidence graphs.

    Requirements:
      1) Preserve the bipartition: vertex-nodes must map to vertex-nodes,
         edge-nodes to edge-nodes.
      2) Additionally, preserve hyperedge size on the edge-side nodes.

    Note:
      - Condition (2) is logically redundant in many cases (degree equals size),
        but making it explicit is safer and can speed up pruning.
    """
    if a.get("bipartite") != b.get("bipartite"):
        return False
    if a.get("bipartite") == 1:
        return a.get("size") == b.get("size")
    return True


def _wl_hash_incidence_graph(B):
    """
    Compute a fast graph-invariant hash (Weisfeiler-Lehman hash) used ONLY for
    'bucketing' candidates before running exact isomorphism checks.

    Important:
      - WL-hash is NOT a complete isomorphism test (it can collide).
      - We use it to reduce the number of expensive GraphMatcher calls.
      - Correctness is guaranteed because we still run exact isomorphism checks
        within each bucket.

    We set node_attr="bipartite" to at least separate the two sides; sizes are
    already encoded as a node attribute on edge nodes, but WL-hash call here
    only uses 'bipartite'. If you want a stronger hash, you may incorporate
    'size' by preprocessing node labels or using a different node_attr scheme.
    """
    try:
        return nx.weisfeiler_lehman_graph_hash(B, node_attr="bipartite", edge_attr=None)
    except Exception:
        # Compatibility with some networkx versions
        from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash
        return weisfeiler_lehman_graph_hash(B, node_attr="bipartite", edge_attr=None)


def _isomorphic_masks(edge_masks_a, n_a, edge_masks_b, n_b):
    """
    Exact hypergraph isomorphism test between two candidates described as masks.

    We:
      1) Build incidence graphs Ba and Bb
      2) Run GraphMatcher with our bipartite-preserving node_match
      3) Return True iff Ba and Bb are isomorphic under that constraint.

    Since we enforce bipartition and edge-size preservation, this corresponds
    to hypergraph isomorphism for our simple hypergraph representation.
    """
    Ba = _incidence_graph_from_masks(edge_masks_a, n_a)
    Bb = _incidence_graph_from_masks(edge_masks_b, n_b)
    gm = GraphMatcher(Ba, Bb, node_match=_node_match)
    return gm.is_isomorphic()


def generate_nonisomorphic_hypergraphs(k, alpha, max_vertices=None, require_no_isolated=True):
    """
    Generate all (simple) hypergraphs up to isomorphism with:
      - exactly k hyperedges
      - each hyperedge size in {1, ..., alpha}
      - number of vertices is not fixed:
          we try all n from 1 up to max_vertices (default: k*alpha)

    Conventions:
      - vertices are labeled 1..n for enumeration purposes
      - we output Hypergraph objects; their vertex set is induced by edges
      - "simple" means no duplicate hyperedges (enforced by combinations)

    Parameter:
      - require_no_isolated:
          if True, we only keep candidates whose edges cover all n vertices,
          i.e., every vertex participates in at least one hyperedge.
          This matches the fact that our Hypergraph class conceptually uses
          only vertices that appear in some edge.

    Efficiency strategy:
      - Enumerate hyperedges on n labeled vertices using bitmasks.
      - Enumerate k-subsets of those hyperedges (no duplicates).
      - Use WL-hash of the incidence graph to bucket candidates quickly.
      - Within each bucket, use exact GraphMatcher isomorphism to keep only
        one representative per isomorphism class.

    Return:
      - list of Hypergraph objects (one representative per isomorphism class).
    """
    if k <= 0:
        raise ValueError("k must be >= 1")
    if alpha <= 0:
        raise ValueError("alpha must be >= 1")

    if max_vertices is None:
        max_vertices = k * alpha
    if max_vertices <= 0:
        return []

    # Dictionary: WL-hash -> list of representatives (n, edge_masks)
    # Each representative stands for an isomorphism class (within that WL bucket
    # we still check exact isomorphism).
    reps_by_hash = {}

    # Try all possible numbers of vertices.
    for n in range(1, max_vertices + 1):
        # Hyperedge size cannot exceed n.
        max_edge_size = min(alpha, n)

        # Bitmask with all n bits set: used to check coverage.
        full_mask = (1 << n) - 1

        # Enumerate all possible hyperedges on {1..n} of size 1..max_edge_size.
        # Represent each hyperedge as an integer bitmask of length n.
        all_edges = []
        for r in range(1, max_edge_size + 1):
            for comb in itertools.combinations(range(n), r):
                m = 0
                for idx in comb:
                    m |= (1 << idx)
                all_edges.append(m)

        # If there are fewer than k distinct hyperedges, no hypergraph exists at this n.
        if len(all_edges) < k:
            continue

        # Enumerate all k-subsets of distinct hyperedges (simple hypergraphs).
        for edge_masks in itertools.combinations(all_edges, k):

            # Optional filter: ensure all vertices 1..n are covered by at least one edge.
            if require_no_isolated:
                union = 0
                for m in edge_masks:
                    union |= m
                if union != full_mask:
                    continue

            # Build incidence graph and compute WL hash for fast bucketing.
            B = _incidence_graph_from_masks(edge_masks, n)
            h = _wl_hash_incidence_graph(B)

            bucket = reps_by_hash.setdefault(h, [])

            # Check exact isomorphism only against current representatives in the same bucket.
            is_new = True
            for (n_rep, masks_rep) in bucket:

                # Different n => cannot be isomorphic under our convention
                # (we are enumerating on exactly n participating vertices).
                if n_rep != n:
                    continue

                if _isomorphic_masks(edge_masks, n, masks_rep, n_rep):
                    is_new = False
                    break

            # If not isomorphic to any known representative in this bucket, keep it.
            if is_new:
                bucket.append((n, edge_masks))

    # Convert all representatives into Hypergraph objects (using vertex labels 1..n).
    out = []
    for bucket in reps_by_hash.values():
        for (n, edge_masks) in bucket:
            edges = [_mask_to_frozenset(m, n) for m in edge_masks]
            H = Hypergraph.from_edges(edges)
            out.append(H)

    return out


def hypergraph_to_set_of_sets_string(H):
    """
    Convert a Hypergraph instance H into a single-line textual representation:
      { {1,2}, {2,3,4}, {5} }

    Notes:
      - We print using integer labels if your hypergraph uses integers.
      - For non-integers, we print their str() values.
      - Sets are printed in a stable order for readability.
    """
    # Sort edges first by size, then lexicographically by stringified vertices.
    def edge_key(e):
        return (len(e), [str(x) for x in sorted(e, key=str)])

    edges_sorted = sorted(H.edges, key=edge_key)

    edge_parts = []
    for e in edges_sorted:
        verts = ", ".join(str(v) for v in sorted(e, key=str))
        edge_parts.append("{" + verts + "}")
    return "{" + ", ".join(edge_parts) + "}"


def write_hypergraphs_to_file(hypergraphs, filepath):
    """
    Write a collection of hypergraphs to a text file, one per line.

    Each line corresponds to ONE isomorphism class representative and is formatted as:
      { {..}, {..}, ... }

    Example line:
      {{1, 2}, {2, 3}}

    Parameters:
      - hypergraphs: iterable of Hypergraph objects
      - filepath: output text file path
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for H in hypergraphs:
            f.write(hypergraph_to_set_of_sets_string(H) + "\n")