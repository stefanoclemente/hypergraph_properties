import re
from collections import defaultdict

from hypergraph_properties.hypergraph import Hypergraph
from hypergraph_properties.venn_graphlets import VennGraphlet3


EDGE_RE = re.compile(r"\{([^{}]*)\}")

# This function reads hyperedges from a file and and outputs a list of hyperedges

def parse_hypergraph_line(line):
    parts = EDGE_RE.findall(line.strip())
    edges = []
    for p in parts:
        items = [x.strip() for x in p.split(",") if x.strip()]
        edges.append({int(x) for x in items})
    return edges

# This function builds a dictionary whose keys are the Venn Diagram and whose values are the hypergraphs that satisfy them


def build_venn_dictionary_from_file(path):
    """
    Returns:
        dict {bitmask: [Hypergraph, Hypergraph, ...]}
    """
    out = defaultdict(list)

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            edges = parse_hypergraph_line(line)
            H = Hypergraph.from_edges(edges)

            bitmask = VennGraphlet3.classify_hypergraph(H).bit_vector()
            out[bitmask].append(H)

    return dict(out)
def print_venn_dictionary(venn_dict):
    for key in sorted(venn_dict):
        print(f"{key}:")
        for H in venn_dict[key]:
            edges = [set(e) for e in H.edges]
            print("  ", edges)
        print()

def write_venn_dictionary_to_file(venn_dict, path):
    with open(path, "w", encoding="utf-8") as f:

        for key in sorted(venn_dict):

            # key can be either a tuple/list of ints OR a string like "[0, 1, ...]"
            if isinstance(key, str):
                key_str = key
            else:
                key_str = str(list(key))

            f.write(f"{key_str}:\n")

            for H in venn_dict[key]:
                edge_strings = []
                for e in H.edges:
                    vertices = ", ".join(str(v) for v in sorted(e))
                    edge_strings.append("{" + vertices + "}")
                line = "{" + ", ".join(edge_strings) + "}"
                f.write("  " + line + "\n")

            f.write("\n")