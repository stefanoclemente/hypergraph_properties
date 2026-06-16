from itertools import product

def is_homomorphism(assignment, H, G):
    """
    Check whether a vertex assignment is a homomorphism from H to G.
    """
    for e in H.edges:
        image = frozenset(assignment[v] for v in e)

        if image not in G.edge_set:
            return False

    return True


def all_assignments(vertices, target_vertices):
    """
    Generate all maps from vertices to target_vertices.

    This is used in the brute-force homomorphism counter, where we need
    to enumerate every possible assignment V(H) -> V(G).
    """
    vertices = list(vertices)
    target_vertices = list(target_vertices)

    if len(vertices) == 0:
        yield {}
        return

    for values in product(target_vertices, repeat=len(vertices)):
        yield dict(zip(vertices, values))

def count_homomorphisms_bruteforce(H, G):
    """
    Count homomorphisms from H to G by exhaustive search.

    This is only meant for testing the dynamic program on small examples.
    """
    count = 0

    for assignment in all_assignments(H.vertices, G.vertices):
        if is_homomorphism(assignment, H, G):
            count += 1

    return count

def freeze_assignment(assignment):
    """
    Return a hashable representation of a vertex assignment.

    The DP table needs assignments as dictionary keys, but Python
    dictionaries are not hashable. We therefore convert an assignment
    such as {'a': 1, 'b': 2} into a canonical tuple.
    """
    return tuple(sorted(assignment.items(), key=lambda x: str(x[0])))


def unfreeze_assignment(frozen_assignment):
    """
    Convert a frozen assignment back into a dictionary.
    """
    return dict(frozen_assignment)


def restrict_assignment(assignment, vertices):
    """
    Restrict a vertex assignment to a given set of vertices by removing
    the corresponding keys of the dictionary.

    This is used when passing information from an edge to one of its
    children in the join tree. Only the vertices shared with the child
    are relevant. 
    """
    return {
        v: assignment[v]
        for v in vertices
        if v in assignment
    }


def extendable_assignments(vertices, G):
    """
    Generate only assignments whose image is contained in some hyperedge of G.
    """
    vertices = list(vertices)
    seen = set()

    if not vertices:
        yield {}
        return

    for target_edge in G.edges:
        for values in product(target_edge, repeat=len(vertices)):
            assignment = dict(zip(vertices, values))
            frozen = freeze_assignment(assignment)

            if frozen not in seen:
                seen.add(frozen)
                yield assignment

def extensions(psi, e, G):
    """
    ATTENTION: IT IS POSSIBLE THAT WE NEED TO MODIFY THIS PART - HOM NOTION
    Generate all extensions of a partial assignment psi on the edge e.
    
    Input:
    
    psi:
        A partial assignment from vertices of e to vertices of G.

    e:
        A hyperedge of H, represented as a frozenset.

    G:
        The target hypergraph.

    Output: 
    
    xi:
        A full assignment from vertices of e to vertices of G such that:
        1) xi extends psi;
        2) the image of e under xi is a hyperedge of G
    """
    fixed_image = set(psi.values())
    unassigned_vertices = [v for v in e if v not in psi]

    for target_edge in G.edges:
        # The already fixed images must be contained in the target edge.
        if not fixed_image.issubset(target_edge):
            continue

        # Assign each still-unassigned vertex of e to a vertex of target_edge.
        for values in product(target_edge, repeat=len(unassigned_vertices)):
            xi = dict(psi)
            xi.update(dict(zip(unassigned_vertices, values)))

            # The image of e under xi is the set of images of its vertices.
            image = frozenset(xi[v] for v in e)

            # We keep only assignments whose image is exactly a hyperedge of G.
            if image == target_edge:
                yield xi

def postorder(root, children):
    """
    Return the nodes of a rooted tree in postorder.

    Every child is returned before its parent.

    Needed for the iterative dynamic programming.
    """
    order = []
    stack = [(root, False)]

    while stack:
        edge_idx, visited = stack.pop()

        if visited:
            order.append(edge_idx)
        else:
            stack.append((edge_idx, True))

            for child_idx in children[edge_idx]:
                stack.append((child_idx, False))

    return order


def count_homomorphisms_acyclic(H, G):
    """
    Count homomorphisms from an alpha-acyclic hypergraph H to G.

    The algorithm uses the join tree of H and performs a bottom-up
    dynamic program over its hyperedges.

    DP[(edge_idx, psi)] stores the number of homomorphisms from the
    subtree rooted at edge_idx, assuming that the vertices shared with
    the parent are mapped according to psi.

    Note: it's iterative. 
    We replace the recursive DP with a iterative DP with topological/postorder order
    """
    root, parent, children = H.join_tree()
    order = postorder(root, children)

    DP = {} #The DP table

    for edge_idx in order: # Edges of the join tree
        e = H.edges[edge_idx]

        # The separator is the intersection with the parent edge.
        # For the root, the separator is empty.
        if parent[edge_idx] is None:
            separator = frozenset()
        else:
            separator = e & H.edges[parent[edge_idx]] # Intersection between two frozensets

        # Enumerate all extendable assignments on the separator.
        for psi in extendable_assignments(separator, G):
            total = 0

            # Enumerate all valid local extensions of psi to the whole edge e.
            for xi in extensions(psi, e, G): #Memo: check whether the notion of "extension" is correct
                contribution = 1

                # Combine the independent contributions of the children.
                for child_idx in children[edge_idx]:
                    child_edge = H.edges[child_idx]
                    child_separator = e & child_edge

                    # The child only sees the assignment on the shared vertices.
                    child_psi = restrict_assignment(xi, child_separator)
                    frozen_child_psi = freeze_assignment(child_psi)

                    contribution *= DP[(child_idx, frozen_child_psi)]

                total += contribution

            DP[(edge_idx, freeze_assignment(psi))] = total

    # At the root, there is no parent separator.
    return DP[(root, freeze_assignment({}))]

def count_homomorphisms(H, G):
    """
    Count homomorphisms from H to G.

    If H is alpha-acyclic, use the join-tree dynamic program.
    Otherwise, fall back to brute force.
    """
    if H.is_alpha_acyclic():
        return count_homomorphisms_acyclic(H, G)

    return count_homomorphisms_bruteforce(H, G)