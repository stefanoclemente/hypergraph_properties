from hypergraph_properties.hypergraph import Hypergraph
from hypergraph_properties.isomorphism import *
from hypergraph_properties.partitions import *
from hypergraph_properties.isomorphism_classes import *
from hypergraph_properties.venn_graphlets import VennGraphlet3
from hypergraph_properties.venn_index import build_venn_dictionary_from_file, write_venn_dictionary_to_file, print_venn_dictionary

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
    alpha1=2
    hs = generate_nonisomorphic_hypergraphs(k=k1, alpha=alpha1)
    #print("Found:", len(hs))
    #for i, H in enumerate(hs):
    #    print("\n===", i, "===")
    #    print(hypergraph_to_set_of_sets_string(H))

    write_hypergraphs_to_file(hs, "tests/hypergraphs_k"+str(k1)+"_"+str(alpha1)+".txt")
    print("\nDone")

def demo3():
    g = VennGraphlet3.from_edges({1, 2}, {2}, {2, 3})
    print(g.describe())
    print(g.is_connected())  

def demo4():
    path = "tests/hypergraphs_k3_3.txt"
    output_path = "tests/hypergraphs_k3_3_indexed.txt"

    venn_dict = build_venn_dictionary_from_file(path)

    for key in sorted(venn_dict):
        print(f"{key}:")
        for H in venn_dict[key]:
            edges = [set(e) for e in H.edges]
            print("  ", edges)
        print()
    write_venn_dictionary_to_file(venn_dict, output_path)

def demo5():
    path = "tests/hypergraphs_k3_3.txt"
    venn_dict = build_venn_dictionary_from_file(path)
    out = {}

    for key, hypergraphs in venn_dict.items():
        if all(H.is_alpha_acyclic() for H in hypergraphs):
            out[key] = hypergraphs

    print_venn_dictionary(out)



if __name__ == "__main__":
    demo5()