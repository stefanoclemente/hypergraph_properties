0. Hypergraph structure (see hypergraphs.py)
==================================================

The file "hypergraphs.py" defines the Hypergraph class used throughout the library.


Required import: 

from hypergraph_properties.hypergraphs import Hypergraph

A hypergraph is represented by:
- a (frozen) set of vertices (vertices can be numbers, strings, any python object)
- a list of hyperedges, each represented as a (frozen)set of vertices

Important:
- duplicate hyperedges are automatically removed.
- empty hyperedges are not allowed.


Hypergraphs can be constructed either by explicitly specifying vertices and edges or directly from a list of hyperedges.

Example1:


    H = Hypergraph(vertices=[0, 1, 2, 3], edges=[{0, 1, 2}, {2, 3}])

Example2:

    H1 = Hypergraph.from_edges([{0, 1, 2}, {2, 3}])
    H2 = Hypergraph.from_edges([{"a", "b", "d"}, {"c", "e"}])
--------------------------------------------------
Core attributes
--------------------------------------------------

- self.vertices
  Set of vertices.

- self.edges
  List of hyperedges, represented as (frozen)sets of vertices.

--------------------------------------------------
Basic methods
--------------------------------------------------

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


==================================================
1. Computing a quotient graph of a hypergraph
==================================================

"Quotient" is a method of the Hypergraph class. Given a Hypergraph object H, it computes 
its quotient hypergraph induced by a vertex partition.

Example:

    partition = [{0, 1}, {2, 3}]
    Hq = H.quotient(partition)


==================================================
2. Hypergraph isomorphism test
==================================================
Required import:

from hypergraph_properties.isomorphism_classes import *

The function "is_isomorphic" checks hypergraph isomorphism between two Hypergraph objects H1 and H2 by running NetworkX GraphMatcher on the bipartite
incidence graphs of H1 and H2.

Example1: 

	is_isomorphic(H1, H2)

Return:
- If return_mapping=False: it returns a Boolean value (True or False)
- If return_mapping=True: it also returns a mapping on the bipartite
    graph node (or None if not isomorphic).

Example2:

	iso = is_isomorphic(H1, H2, return_mapping=False)
	iso, mapping = is_isomorphic(H1, H2, return_mapping=True)

==================================================
3. Hypergraph automorphisms 
==================================================

Required import:

from hypergraph_properties.isomorphism_classes import *

The function "hypergraph_automorphisms" computes vertex automorphisms of H and returns a dictionary (mapping) ('v': v), 
each one representing an automorphism of H.

Example:
autos = hypergraph_automorphisms(H)

To compute the number of automorphism, just compute the length of the list (len(autos)).

==================================================
4. Venn graphlets
==================================================
Required import: 

from hypergraph_properties.venn_graphlets import VennGraphlet3


Venn graphlets are represented 

To build a VennGraphlet from three edges (of any size):


- VennGraphlet3.from_edges(e1, e2, e3)


Example:

	g = VennGraphlet3.from_edges({1, 2, 3}, {3, 4}, {1, 4})

Useful functions:

--------------------------------------------------
VennGraphlet3.classify_hypergraph(H)
--------------------------------------------------

Given a hypergraph H, its corresponding Venn graphlet (diagram) can be computed in the following way:


- g = VennGraphlet3.classify_hypergraph(H)


Example:
	H = Hypergraph.from_edges([{0, 1, 2}, {2, 3}, {4, 5, 6}])
 	g = VennGraphlet3.classify_hypergraph(H)

--------------------------------------------------
VennGraphlet3.describe()
--------------------------------------------------

Returns a short human-readable description of which regions (patterns of intersection) are present.

Example:
	
	s = g.describe()

--------------------------------------------------
VennGraphlet3.matches_hypergraph(H)
--------------------------------------------------

Returns

Example:
	H = Hypergraph.from_edges([{0, 1, 2}, {2, 3}, {4, 5, 6}])
	g = VennGraphlet3.from_edges({1, 2, 3}, {3, 4}, {1, 4})
	g.matches_hypergraph(H)

==================================================
5. Generation of non-isomorphic hypergraphs
==================================================
Required import:

from hypergraph_properties.isomorphism_classes import *

- To generate a python list all non-isomorphic hypergraphs with arity alpha1 and number of edge k1:

	
	hs = generate_nonisomorphic_hypergraphs(k=k1, alpha=alpha1)

- to list them in a .txt file (why: so you do not need to recompute them):

	write_hypergraphs_to_file(hs, "hypergraphs_k"+str(k1)+"_"+str(alpha1)+".txt")