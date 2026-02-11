# Hypergraph Properties Library

## 0. Hypergraph Structure (see hypergraphs.py)

The file `hypergraphs.py` defines the Hypergraph class used throughout the library.

### Required import

    from hypergraph_properties.hypergraphs import Hypergraph

### Hypergraph representation

A hypergraph is represented by:
- a (frozen) set of vertices (vertices can be numbers, strings, any python object)
- a list of hyperedges, each represented as a (frozen) set of vertices

Important:
- duplicate hyperedges are automatically removed
- empty hyperedges are not allowed

### Construction

Hypergraphs can be constructed either by explicitly specifying vertices and edges or directly from a list of hyperedges.

Example 1:

    H = Hypergraph(vertices=[0, 1, 2, 3], edges=[{0, 1, 2}, {2, 3}])

Example 2:

    H1 = Hypergraph.from_edges([{0, 1, 2}, {2, 3}])
    H2 = Hypergraph.from_edges([{"a", "b", "d"}, {"c", "e"}])

### Core attributes

- self.vertices  
  Set of vertices.

- self.edges  
  List of hyperedges, represented as (frozen) sets of vertices.

### Basic methods

- add_vertex(v, **attrs)  
  Adds a vertex and optional attributes.

- add_edge(nodes, **attrs)  
  Adds a hyperedge; returns its index or None if the edge already exists.

- num_vertices()  
  Returns the number of vertices.

- num_edges()  
  Returns the number of hyperedges.

- edge_sizes()  
  Returns a list with the size of each hyperedge.

- degree(v)  
  Returns the degree of vertex v.

## 1. Computing a Quotient Graph of a Hypergraph

The method `quotient` of the Hypergraph class computes the quotient hypergraph induced by a vertex partition.

Example:

    partition = [{0, 1}, {2, 3}]
    Hq = H.quotient(partition)

## 2. Hypergraph Isomorphism Test

### Required import

from hypergraph_properties.isomorphism_classes import *

The function `is_isomorphic` checks hypergraph isomorphism between two Hypergraph objects H1 and H2 by running NetworkX GraphMatcher on the bipartite incidence graphs of H1 and H2.

Example 1:

    is_isomorphic(H1, H2)

Return:
- If return_mapping=False: it returns a Boolean value (True or False)
- If return_mapping=True: it also returns a mapping on the bipartite graph nodes (or None if not isomorphic)

Example 2:

    iso = is_isomorphic(H1, H2, return_mapping=False)
    iso, mapping = is_isomorphic(H1, H2, return_mapping=True)

## 3. Hypergraph Automorphisms

### Required import

from hypergraph_properties.isomorphism_classes import *

The function `hypergraph_automorphisms` computes vertex automorphisms of H and returns a list of dictionaries, each one representing an automorphism of H.

Example:

    autos = hypergraph_automorphisms(H)

To compute the number of automorphisms:

    len(autos)

## 4. Venn Graphlets

### Required import

from hypergraph_properties.venn_graphlets import VennGraphlet3

Venn graphlets are constructed from three edges of arbitrary size.

To build a VennGraphlet:

    g = VennGraphlet3.from_edges(e1, e2, e3)

Example:

    g = VennGraphlet3.from_edges({1, 2, 3}, {3, 4}, {1, 4})

### Classify a hypergraph

Given a hypergraph H, its corresponding Venn graphlet can be computed as follows:

    g = VennGraphlet3.classify_hypergraph(H)

Example:

    H = Hypergraph.from_edges([{0, 1, 2}, {2, 3}, {4, 5, 6}])
    g = VennGraphlet3.classify_hypergraph(H)

### Describe a Venn graphlet

Returns a short human-readable description of which regions (patterns of intersection) are present.

    s = g.describe()

### Match a hypergraph

Checks whether a hypergraph matches the Venn graphlet pattern.

Example:

    g.matches_hypergraph(H)

## 5. Generation of Non-Isomorphic Hypergraphs

### Required import

from hypergraph_properties.isomorphism_classes import *

To generate a list of all non-isomorphic hypergraphs with arity alpha1 and number of edges k1:

    hs = generate_nonisomorphic_hypergraphs(k=k1, alpha=alpha1)

To save them to a text file:

    write_hypergraphs_to_file(hs,"hypergraphs_k" + str(k1) + "_" + str(alpha1) +".txt")