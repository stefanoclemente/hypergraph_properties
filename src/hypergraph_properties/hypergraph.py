class Hypergraph:
    """
    Minimal hypergraph H = (V, E) focused on quotient hypergraph construction w.r.t. a vertex partition

    Hyperedges are represented as immutable sets - i.e. frozensets. 
    
    Why sets: efficiency, as long as we do not require any internal sorting of the vertices

    Why frozensets: more memory-efficient than sets, hashable.


    """

    def __init__(self, vertices=None, edges=None, vertex_attrs=None, edge_attrs=None):
        self.vertices = set(vertices) if vertices is not None else set()
        self.edges = []
        self.edge_attrs = []
        self.edge_set = set()
        self.vertex_attrs = dict(vertex_attrs) if vertex_attrs is not None else {}

        if edges is not None:
            for e in edges:
                fe = frozenset(e)
                if len(fe) == 0:
                    raise ValueError("Empty hyperedges are not allowed.")
                if fe in self.edge_set:
                    continue
                self.edge_set.add(fe)
                self.edges.append(fe)

        if edge_attrs is None:
            self.edge_attrs = [{} for _ in self.edges]
        else:
            if len(edge_attrs) != len(self.edges):
                raise ValueError("edge_attrs must have the same length as edges.")
            self.edge_attrs = [dict(a) for a in edge_attrs]

        for e in self.edges:
            self.vertices.update(e)

    @classmethod
    def from_edges(cls, edge_sets, vertex_attrs=None, edge_attrs=None):
        edges = []
        for s in edge_sets:
            e = frozenset(s)
            if len(e) == 0:
                raise ValueError("Empty hyperedges are not allowed.")
            edges.append(e)
        return cls(vertices=None, edges=edges, vertex_attrs=vertex_attrs, edge_attrs=edge_attrs)

    def add_vertex(self, v, **attrs):
        self.vertices.add(v)
        if attrs:
            self.vertex_attrs.setdefault(v, {}).update(attrs)

    def add_edge(self, nodes, **attrs):
        e = frozenset(nodes)
        if len(e) == 0:
            raise ValueError("Empty hyperedges are not allowed.")
        if e in self.edge_set:
            return None
        self.edge_set.add(e)
        self.edges.append(e)
        self.edge_attrs.append(dict(attrs))
        self.vertices.update(e)
        return len(self.edges) - 1

    def num_vertices(self):
        return len(self.vertices)

    def num_edges(self):
        return len(self.edges)

    def edge_sizes(self):
        return [len(e) for e in self.edges]

    def degree(self, v):
        return sum(1 for e in self.edges if v in e)

    def __str__(self):
        lines = []
        lines.append("Hypergraph:")
        lines.append(f"  |V| = {len(self.vertices)}")
        lines.append(f"  |E| = {len(self.edges)}")
        lines.append("  Vertices:")
        for v in sorted(self.vertices, key=str):
            lines.append(f"    - {v}")
        lines.append("  Hyperedges:")
        for i, e in enumerate(self.edges):
            nodes = ", ".join(str(v) for v in sorted(e, key=str))
            lines.append(f"    e{i}: {{{nodes}}}")
        return "\n".join(lines)

    def pretty_print(self):
        print(self)

    def quotient(self, partition):
        from .partitions import normalize_partition, validate_partition, vertex_to_block_map

        blocks = normalize_partition(partition)
        validate_partition(blocks, self.vertices)
        v2blk = vertex_to_block_map(blocks)

        Hq = Hypergraph(vertices=set(blocks), edges=[], vertex_attrs=None, edge_attrs=[])
        for e in self.edges:
            q_edge = frozenset(v2blk[v] for v in e)
            Hq.add_edge(q_edge)
        return Hq
    
    def is_alpha_acyclic(self):
        """
        Check alpha-acyclicity via GYO reduction.

        Returns True iff the GYO reduction eliminates all hyperedges.
        """
        # Work on a mutable copy of the edge family
        edges = [set(e) for e in self.edges]

        # If there are no edges, treat as alpha-acyclic
        if not edges:
            return True

        changed = True
        while changed:
            changed = False

            # Step1: remove vertices that appear in <= 1 hyperedge
            counts = {}
            for e in edges:
                for v in e:
                    counts[v] = counts.get(v, 0) + 1

            removable = {v for v, c in counts.items() if c <= 1}
            if removable:
                for e in edges:
                    e.difference_update(removable)
                changed = True

            # Step2: remove empty edges created by vertex deletions
            new_edges = [e for e in edges if len(e) > 0]
            if len(new_edges) != len(edges):
                edges = new_edges
                changed = True
            else:
                edges = new_edges

            if not edges:
                return True

            # Step3: remove edges contained in other edges ----
            to_remove = set()
            for i in range(len(edges)):
                if i in to_remove:
                    continue
                ei = edges[i]
                for j in range(len(edges)):
                    if i == j or j in to_remove:
                        continue
                    ej = edges[j]
                    if ei.issubset(ej):
                        to_remove.add(i)
                        break

            if to_remove:
                edges = [e for idx, e in enumerate(edges) if idx not in to_remove]
                changed = True

        # If reduction stops with non-empty edges, not alpha-acyclic
        return len(edges) == 0
    