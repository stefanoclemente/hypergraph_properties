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
    
    def join_tree1(self):
        """
        Build a join tree via GYO reduction.

        Returns
        -------
        root:
            Index of the root hyperedge.

        parent:
            Dictionary mapping each hyperedge index to its parent index.

        children:
            Dictionary mapping each hyperedge index to its children.

        Raises
        ------
        ValueError
            If the hypergraph is not alpha-acyclic.
        """
        # Work on a mutable copy of the edge family, keeping original indices
        edges = [(idx, set(e)) for idx, e in enumerate(self.edges)]

        # If there are no edges, there is no join tree to build
        if not edges:
            raise ValueError("Cannot build a join tree of a hypergraph with no edges.")

        # If there is only one hyperedge, the join tree is a single node
        if len(edges) == 1:
            return 0, {0: None}, {0: []}

        # Undirected adjacency list of the join tree
        tree = {idx: set() for idx in range(len(self.edges))}

        changed = True
        while changed:
            changed = False

            # Step1: remove vertices that appear in <= 1 hyperedge
            counts = {}
            for _, e in edges:
                for v in e:
                    counts[v] = counts.get(v, 0) + 1

            removable = {v for v, c in counts.items() if c <= 1}
            if removable:
                for _, e in edges:
                    e.difference_update(removable)
                changed = True

            # Step2: remove empty edges created by vertex deletions
            new_edges = [(idx, e) for idx, e in edges if len(e) > 0]

            # If an edge becomes empty, attach it to any remaining active edge.
            # This mirrors the GYO deletion, but also records a join-tree edge.
            empty_edges = [(idx, e) for idx, e in edges if len(e) == 0]

            if empty_edges and new_edges:
                parent_idx = new_edges[0][0]

                for idx, _ in empty_edges:
                    tree[idx].add(parent_idx)
                    tree[parent_idx].add(idx)

                edges = new_edges
                changed = True
            else:
                edges = new_edges

            if len(edges) == 1:
                break

            # Step3: remove edges contained in other edges
            to_remove = set()
            contains = {}

            for i in range(len(edges)):
                if i in to_remove:
                    continue

                idx_i, ei = edges[i]

                for j in range(len(edges)):
                    if i == j or j in to_remove:
                        continue

                    idx_j, ej = edges[j]

                    if ei.issubset(ej):
                        to_remove.add(i)
                        contains[i] = j
                        break

            if to_remove:
                for i in to_remove:
                    j = contains[i]

                    idx_i, _ = edges[i]
                    idx_j, _ = edges[j]

                    # If edge i is contained in edge j, connect their
                    # original hyperedges in the join tree.
                    tree[idx_i].add(idx_j)
                    tree[idx_j].add(idx_i)

                edges = [
                    edge
                    for i, edge in enumerate(edges)
                    if i not in to_remove
                ]
                changed = True

        # If reduction stops with more than one active edge, no join tree exists
        if len(edges) != 1:
            raise ValueError("The hypergraph is not alpha-acyclic.")

        # Root the constructed join tree at the last remaining hyperedge
        root = edges[0][0]
        parent = {root: None}
        children = {idx: [] for idx in range(len(self.edges))}

        stack = [root]

        while stack:
            idx = stack.pop()

            for other in tree[idx]:
                if other == parent.get(idx):
                    continue

                parent[other] = idx
                children[idx].append(other)
                stack.append(other)

        return root, parent, children
    
    def join_tree(self):
        """
        Build a join tree using a GYO-style reduction.

        The nodes of the join tree are the hyperedges of the hypergraph,
        represented by their indices in self.edges.

        Returns
        -------
        root:
            Index of the root hyperedge.

        parent:
            Dictionary mapping each hyperedge index to its parent index.
            The root has parent None.

        children:
            Dictionary mapping each hyperedge index to its children.

        Raises
        ------
        ValueError
            If the hypergraph is not alpha-acyclic.
        """
        edges = [(idx, set(e)) for idx, e in enumerate(self.edges)]

        if not edges:
            raise ValueError("Cannot build a join tree of a hypergraph with no edges.")

        if len(edges) == 1:
            return 0, {0: None}, {0: []}

        tree = {idx: set() for idx in range(len(self.edges))}
        last_removed = None

        changed = True

        while changed:
            changed = False

            # Step 1: remove vertices that appear in at most one hyperedge.
            counts = {}

            for _, e in edges:
                for v in e:
                    counts[v] = counts.get(v, 0) + 1

            removable = {v for v, c in counts.items() if c <= 1}

            if removable:
                for _, e in edges:
                    e.difference_update(removable)

                changed = True

            # Step 2: remove empty hyperedges.
            new_edges = [(idx, e) for idx, e in edges if len(e) > 0]
            empty_edges = [(idx, e) for idx, e in edges if len(e) == 0]

            if empty_edges:
                if new_edges:
                    # Attach every empty edge to an arbitrary remaining active edge.
                    parent_idx = new_edges[0][0]

                    for idx, _ in empty_edges:
                        tree[idx].add(parent_idx)
                        tree[parent_idx].add(idx)
                        last_removed = idx

                else:
                    # All remaining edges became empty at the same time.
                    # They can be connected arbitrarily.
                    root_idx = empty_edges[0][0]
                    last_removed = root_idx

                    for idx, _ in empty_edges[1:]:
                        tree[root_idx].add(idx)
                        tree[idx].add(root_idx)
                        last_removed = idx

                edges = new_edges
                changed = True

            if len(edges) == 0:
                break

            # Step 3: remove hyperedges contained in other hyperedges.
            to_remove = set()
            contains = {}

            for i in range(len(edges)):
                if i in to_remove:
                    continue

                idx_i, ei = edges[i]

                for j in range(len(edges)):
                    if i == j or j in to_remove:
                        continue

                    idx_j, ej = edges[j]

                    if ei.issubset(ej):
                        to_remove.add(i)
                        contains[i] = j
                        break

            if to_remove:
                for i in to_remove:
                    j = contains[i]

                    idx_i, _ = edges[i]
                    idx_j, _ = edges[j]

                    # If edge i is contained in edge j, connect them in the join tree.
                    tree[idx_i].add(idx_j)
                    tree[idx_j].add(idx_i)

                    last_removed = idx_i

                edges = [
                    edge
                    for i, edge in enumerate(edges)
                    if i not in to_remove
                ]

                changed = True

        # If GYO did not remove all edges, the hypergraph is not alpha-acyclic.
        if edges:
            raise ValueError("The hypergraph is not alpha-acyclic.")

        if last_removed is None:
            raise ValueError("Could not build a join tree.")

        # Root the constructed join tree.
        root = last_removed
        parent = {root: None}
        children = {idx: [] for idx in range(len(self.edges))}

        stack = [root]
        visited = set()

        while stack:
            idx = stack.pop()
            visited.add(idx)

            for other in tree[idx]:
                if other == parent.get(idx):
                    continue

                parent[other] = idx
                children[idx].append(other)
                stack.append(other)

        if len(visited) != len(self.edges):
            raise ValueError("Could not build a connected join tree.")

        return root, parent, children