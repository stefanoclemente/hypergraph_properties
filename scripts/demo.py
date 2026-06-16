from hypergraph_properties.hypergraph import Hypergraph
from hypergraph_properties.isomorphism import *
from hypergraph_properties.partitions import *
from hypergraph_properties.homomorphisms import *
from hypergraph_properties.isomorphism_classes import *
from hypergraph_properties.venn_graphlets import VennGraphlet3
from hypergraph_properties.venn_index import build_venn_dictionary_from_file, write_venn_dictionary_to_file, print_venn_dictionary, read_graphlets_from_file
from hypergraph_properties.edge_sub_count import count_edge_subgraphs_via_formula
import time 

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
    output_path = "tests/hypergraphs_k3_3_acyclic.txt"
    venn_dict = build_venn_dictionary_from_file(path)
    out = {}

    for key, hypergraphs in venn_dict.items():
        if all(H.is_alpha_acyclic() for H in hypergraphs):
            out[key] = hypergraphs

    write_venn_dictionary_to_file(out, output_path)

def demo6():
    print("Demo 6: homomorphism counting on acyclic hypergraphs")

    H = Hypergraph.from_edges([
    {1, 2},
    {2, 3},
    {3, 4},
])
    G = Hypergraph.from_edges([{"a", "b"}, {"b", "c"}, {"a", "c"}])

    print("\nPattern H:")
    print(H)

    print("\nTarget G:")
    print(G)

    dp_count = count_homomorphisms_acyclic(H, G)
    brute_force_count = count_homomorphisms_bruteforce(H, G)

    print("\nDP count:", dp_count)
    print("Brute-force count:", brute_force_count)
    print("Correct?", dp_count == brute_force_count)

def demo7():
    print("Demo 7: homomorphism counting with larger hyperedges")

    H = Hypergraph.from_edges([
        {1, 2, 3},
        {3, 4},
    ])

    G = Hypergraph.from_edges([
        {"a", "b", "c"},
        {"c", "d"},
        {"a", "c"},
        {"b", "d"},
    ])

    print("\nPattern H:")
    print(H)

    print("\nTarget G:")
    print(G)

    print("\nH is alpha-acyclic:", H.is_alpha_acyclic())

    dp_count = count_homomorphisms_acyclic(H, G)
    brute_force_count = count_homomorphisms_bruteforce(H, G)

    print("\nDP count:", dp_count)
    print("Brute-force count:", brute_force_count)
    print("Correct?", dp_count == brute_force_count)


def demo8():
    print("Demo 8: timing DP vs brute force")

    H = Hypergraph.from_edges([
        {1, 2},
        {2, 3},
        {3, 4},
        {4, 5},
        {5, 6},
        {6, 7},
    ])

    G = Hypergraph.from_edges([
        {"a", "b"},
        {"b", "c"},
        {"c", "d"},
        {"d", "e"},
        {"e", "f"},
        {"f", "g"},
        {"a", "c"},
        {"b", "d"},
        {"c", "e"},
        {"d", "f"},
        {"e", "g"},
    ])

    print("\nPattern H:")
    print(H)

    print("\nTarget G:")
    print(G)

    print("\nH is alpha-acyclic:", H.is_alpha_acyclic())

    start = time.perf_counter()
    dp_count = count_homomorphisms_acyclic(H, G)
    dp_time = time.perf_counter() - start

    start = time.perf_counter()
    brute_force_count = count_homomorphisms_bruteforce(H, G)
    brute_force_time = time.perf_counter() - start

    print("\nDP count:", dp_count)
    print("Brute-force count:", brute_force_count)
    print("Correct?", dp_count == brute_force_count)

    print("\nDP time:", dp_time)
    print("Brute-force time:", brute_force_time)

def demo9():
    print("Demo 9: evaluating formula (6) on acyclic 3-edge graphlets")

    path = "tests/hypergraphs_k3_3_acyclic.txt"
    graphlets = read_graphlets_from_file(path) # This part needs to be modified. These are not the graphlets we need.

    G = Hypergraph.from_edges([
        {"a", "b"},
        {"b", "c"},
        {"c", "d"},
        {"d", "e"},
        {"a", "c"},
        {"b", "d"},
        {"c", "e"},
        {"a", "b", "c"},
        {"b", "c", "d"},
        {"c", "d", "e"},
    ])

    print("\nNumber of graphlets:", len(graphlets))
    print("All graphlets alpha-acyclic:", all(H.is_alpha_acyclic() for H in graphlets))

    print("\nTarget G:")
    print(G)

    start = time.perf_counter()
    count = count_edge_subgraphs_via_formula(graphlets, G)
    elapsed = time.perf_counter() - start

    print("\nFormula count:", count)
    print("Time:", elapsed)



if __name__ == "__main__":
    demo9()