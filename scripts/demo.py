from hypergraph_properties.hypergraph import Hypergraph
from hypergraph_properties.isomorphism import *
from hypergraph_properties.partitions import *
from hypergraph_properties.isomorphism_classes import *
from hypergraph_properties.venn_graphlets import VennGraphlet3

def demo1():
    H = Hypergraph.from_edges([{1, 2, 3}, {3, 4}, {2, 4}])
    print(H)

    tau = [{1, 2}, {3}, {4}]
    Hq = H.quotient(tau)
    print("\nQuotient:")
    print(Hq)

    G = Hypergraph.from_edges([{"a", "b", "c"}, {"c", "d"}, {"b", "d"}])
    iso, mapping = is_isomorphic(H, G, return_mapping=True)
    print("\nIsomorphic?", iso)
    if iso:
        vmap = induced_vertex_mapping_from_incidence_mapping(mapping)
        print("Vertex mapping:", vmap)

    H2 = Hypergraph.from_edges([{1, 2}, {2, 3}])
    autos = hypergraph_automorphisms(H2)
    print("\nAutomorphisms:", autos)

def demo2():
    k1=3
    alpha1=3
    hs = generate_nonisomorphic_hypergraphs(k=k1, alpha=alpha1)
    #print("Found:", len(hs))
    #for i, H in enumerate(hs):
    #    print("\n===", i, "===")
    #    print(hypergraph_to_set_of_sets_string(H))

    write_hypergraphs_to_file(hs, "hypergraphs_k"+str(k1)+"_"+str(alpha1)+".txt")
    print("\nWrote to hypergraphs_k2_a2.txt")

def demo3():
    g = VennGraphlet3.from_edges({1, 3, 4}, {2, 3}, {1, 2, 3})
    print(g.bits())       
    print(g.describe())   


if __name__ == "__main__":
    demo2()