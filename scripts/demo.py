from hypergraph_properties.hypergraph import Hypergraph
from hypergraph_properties.isomorphism import (
    is_isomorphic,
    induced_vertex_mapping_from_incidence_mapping,
    hypergraph_automorphisms,
)

def main():
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


if __name__ == "__main__":
    main()