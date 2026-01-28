import math
def normalize_partition(partition):
    blocks = []
    for blk in partition:
        f = frozenset(blk)
        if len(f) == 0:
            raise ValueError("Partition blocks must be non-empty.")
        blocks.append(f)
    return blocks


def validate_partition(blocks, vertices):
    union = set()
    for blk in blocks:
        if union.intersection(blk):
            raise ValueError("Partition is not disjoint (some blocks intersect).")
        union.update(blk)

    if union != vertices:
        missing = vertices - union
        extra = union - vertices
        parts = []
        if missing:
            parts.append(f"missing vertices: {sorted(missing, key=str)}")
        if extra:
            parts.append(f"extra vertices: {sorted(extra, key=str)}")
        raise ValueError("Partition does not cover exactly V (" + ", ".join(parts) + ").")


def vertex_to_block_map(blocks):
    v2blk = {}
    for blk in blocks:
        for v in blk:
            v2blk[v] = blk
    return v2blk


def all_partitions(n):
    if n <= 0:
        return [[]]
    if n == 1:
        return [[{1}]]

    prev_partitions = all_partitions(n - 1)
    result = []

    for part in prev_partitions:
        new_part = [block.copy() for block in part]
        new_part.append({n})
        result.append(new_part)

        for i in range(len(part)):
            new_part = [block.copy() for block in part]
            new_part[i].add(n)
            result.append(new_part)

    return result

def moebius_function(partition):
    """
    Compute the moebius function for a given partition rho:
    mu(rho) = (-1)^(|rho|-1) * (|rho|-1)!
    """
    rho = len(partition)
    return (-1) ** (rho - 1) * math.factorial(rho - 1)