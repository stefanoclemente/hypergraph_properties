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

def vertex_partitions(vertices):
    """
    Generate all partitions of the given vertex set.

    This wraps all_partitions(n), which generates partitions of {1, ..., n},
    and converts them into partitions of the actual vertices.
    """
    vertices = list(vertices)

    for partition in all_partitions(len(vertices)):
        converted_partition = []

        for block in partition:
            converted_block = {vertices[i - 1] for i in block}
            converted_partition.append(converted_block)

        yield converted_partition

def moebius_function_top(partition):
    """
    Computes the top moebius function for a given partition rho:
    mu(rho) = (-1)^(|rho|-1) * (|rho|-1)!
    """
    rho = len(partition)
    return (-1) ** (rho - 1) * math.factorial(rho - 1)

def moebius_function(partition):
    """
    Computes the bottom Möbius function where each block B contributes
    (-1)^(|B|-1) * (|B|-1)!.
    """
    result = 1

    for block in partition:
        size = len(block)
        result *= (-1) ** (size - 1) * math.factorial(size - 1)

    return result