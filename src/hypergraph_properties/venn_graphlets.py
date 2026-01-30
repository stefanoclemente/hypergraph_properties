from itertools import permutations


def _regions_signature(A, B, C):
    """
    Compute the 7-bit Venn signature for three sets A, B, C.

    Each bit encodes whether a specific Venn region is non-empty (1) or empty (0).
    Bit order (least significant bit = region 1):

        bit 0 -> A \ B \ C              (only e1)
        bit 1 -> B \ C \ A              (only e2)
        bit 2 -> C \ A \ B              (only e3)
        bit 3 -> A ∩ B \ C              (e1 and e2 only)
        bit 4 -> B ∩ C \ A              (e2 and e3 only)
        bit 5 -> C ∩ A \ B              (e3 and e1 only)
        bit 6 -> A ∩ B ∩ C              (triple intersection)

    The signature is therefore an integer in [0, 127] whose binary
    representation describes the emptiness pattern of the 7 regions.
    """

    r1 = A - B - C #  The difference operation on sets. The results is 0 iff the difference is the empty set.
    r2 = B - C - A
    r3 = C - A - B
    r4 = (A & B) - C
    r5 = (B & C) - A
    r6 = (C & A) - B
    r7 = A & B & C

    bits = [
        1 if r1 else 0,
        1 if r2 else 0,
        1 if r3 else 0,
        1 if r4 else 0,
        1 if r5 else 0,
        1 if r6 else 0,
        1 if r7 else 0,
    ]

    sig = 0
    for i, b in enumerate(bits):
        sig |= (b << i)
    return sig


def _permute_signature(sig, perm):
    """
    Given a 7-bit signature computed for (A, B, C), return the signature obtained
    after permuting the roles of the three sets.

    perm is a permutation of (0, 1, 2) meaning:
        new A = old set perm[0]
        new B = old set perm[1]
        new C = old set perm[2]

    This is used internally to make the signature invariant with respect to the
    ordering of the three hyperedges.
    """
    b = [(sig >> i) & 1 for i in range(7)]

    # Mapping from logical regions to bit indices in the original signature.
    # only(A)=0, only(B)=1, only(C)=2
    # AB-only=3, BC-only=4, CA-only=5, ABC=6
    only = {0: 0, 1: 1, 2: 2}
    pair = {
        (0, 1): 3, (1, 0): 3,
        (1, 2): 4, (2, 1): 4,
        (2, 0): 5, (0, 2): 5,
    }
    triple = 6

    p0, p1, p2 = perm
    new_bits = [0] * 7

    # Single-set regions
    new_bits[0] = b[only[p0]]
    new_bits[1] = b[only[p1]]
    new_bits[2] = b[only[p2]]

    # Pairwise intersections
    new_bits[3] = b[pair[(p0, p1)]]
    new_bits[4] = b[pair[(p1, p2)]]
    new_bits[5] = b[pair[(p2, p0)]]

    # Triple intersection is invariant under permutation
    new_bits[6] = b[triple]

    out = 0
    for i, bit in enumerate(new_bits):
        out |= (bit << i)
    return out


def canonical_signature(sig):
    """
    Return the canonical (order-invariant) version of a signature.

    The canonical signature is defined as the minimum integer among all
    signatures obtained by permuting the three hyperedges (6 permutations).

    Two Venn patterns are considered equivalent if and only if they have
    the same canonical signature.
    """
    best = None
    for perm in permutations((0, 1, 2), 3):
        s2 = _permute_signature(sig, perm)
        best = s2 if best is None else min(best, s2)
    return best


class VennGraphlet3:
    """
    Venn-based graphlet for k = 3 hyperedges.

    The structure is fully characterized by a 7-bit signature describing
    which Venn regions are empty or non-empty.

    Attributes:
        - e1, e2, e3:
            The three hyperedges as frozensets (only stored for reference).

        - raw_signature:
            7-bit signature for the given ordering (e1, e2, e3).

        - signature:
            Canonical 7-bit signature, invariant under permutations of
            (e1, e2, e3). This is the main identifier of the graphlet.

        - motif_id:
            Optional external label (e.g., 1..26 from the paper), if provided
            via a lookup table.
    """

    def __init__(self, e1, e2, e3, raw_signature, signature):
        self.e1 = e1
        self.e2 = e2
        self.e3 = e3
        self.raw_signature = raw_signature
        self.signature = signature

    @staticmethod
    def from_edges(e1, e2, e3):
        """
        Build a VennGraphlet3 from three iterable edge objects.

        The canonical (order-invariant) signature is always used.
        Optionally, a dictionary signature_to_id can be provided to map
        canonical signatures to external motif identifiers.
        """
        A = frozenset(e1)
        B = frozenset(e2)
        C = frozenset(e3)

        raw = _regions_signature(A, B, C)
        sig = canonical_signature(raw)


        return VennGraphlet3(A, B, C, raw_signature=raw, signature=sig)

    @staticmethod
    def classify_hypergraph(H):
        """
        Build a VennGraphlet3 directly from a Hypergraph instance H.

        H must contain exactly 3 hyperedges.
        """
        if H.num_edges() != 3:
            raise ValueError("Expected exactly 3 hyperedges in the Hypergraph.")

        e1, e2, e3 = H.edges[0], H.edges[1], H.edges[2]
        return VennGraphlet3.from_edges(
            e1, e2, e3
        )

    def bits(self):
        """
        Return the 7 canonical signature bits as a tuple.

        bit i = 1 means that region (i+1) is non-empty.
        """
        s = self.signature
        return tuple((s >> i) & 1 for i in range(7))

    def describe(self):
        """
        Human-readable description using the color convention:

        - Regions belonging to exactly one hyperedge:
              "green zone of eX"

        - Regions belonging to exactly two hyperedges:
              "blue zone of eX and eY"

        - Triple intersection:
              "red zone (e1, e2, e3)"

        This description is meant for quick qualitative inspection of the
        graphlet structure.
        """
        s = self.signature
        present = [(s >> i) & 1 for i in range(7)]

        parts = []

        # Single-edge regions -> green
        if present[0]:
            parts.append("a green zone of e1")
        if present[1]:
            parts.append("a green zone of e2")
        if present[2]:
            parts.append("a green zone of e3")

        # Pairwise regions -> blue
        if present[3]:
            parts.append("a blue zone of e1 and e2")
        if present[4]:
            parts.append("a blue zone of e2 and e3")
        if present[5]:
            parts.append("a blue zone of e3 and e1")

        # Triple region -> red
        if present[6]:
            parts.append("a red zone (e1, e2, e3)")

        if not parts:
            return "No zones present (this should not happen for valid hyperedges)."

        if len(parts) == 1:
            return parts[0] + "."

        return ", ".join(parts[:-1]) + " and " + parts[-1] + "."

    def matches_hypergraph(self, H):
        """
        Return True if the given Hypergraph H matches this graphlet.

        Matching is performed by comparing canonical signatures.
        """
        g = VennGraphlet3.classify_hypergraph(H)
        return g.signature == self.signature

    def __str__(self):
        return f"VennGraphlet3(signature={self.signature:07b}, motif_id={self.motif_id})"
