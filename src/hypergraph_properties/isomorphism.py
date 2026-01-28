import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

from .hypergraph import Hypergraph


def node_match_bipartite(a, b):
    return a.get("bipartite") == b.get("bipartite")


def to_bipartite_graph(H):
    B = nx.Graph()

    for v in H.vertices:
        B.add_node(("v", v), bipartite=0)

    for eid, e in enumerate(H.edges):
        enode = ("e", eid)
        B.add_node(enode, bipartite=1, size=len(e))
        for v in e:
            B.add_edge(enode, ("v", v))

    return B


def is_isomorphic(H1, H2, return_mapping=False):
    B1 = to_bipartite_graph(H1)
    B2 = to_bipartite_graph(H2)

    gm = GraphMatcher(B1, B2, node_match=node_match_bipartite)
    iso = gm.is_isomorphic()

    if not return_mapping:
        return iso
    return iso, (gm.mapping if iso else None)


def induced_vertex_mapping_from_incidence_mapping(incidence_mapping):
    out = {}
    for k, v in incidence_mapping.items():
        if isinstance(k, tuple) and len(k) == 2 and k[0] == "v":
            out[k[1]] = v[1]
    return out


def hypergraph_automorphisms(H, limit=None):
    B = to_bipartite_graph(H)
    gm = GraphMatcher(B, B, node_match=node_match_bipartite)

    autos = []
    for mapping in gm.isomorphisms_iter():
        vmap = induced_vertex_mapping_from_incidence_mapping(mapping)
        autos.append(vmap)

        if limit is not None and len(autos) >= limit:
            break

    return autos