from fractions import Fraction

from hypergraph_properties.isomorphism import is_isomorphic, find_isomorphic_representative, hypergraph_automorphisms
from hypergraph_properties.partitions import vertex_partitions, moebius_function
from hypergraph_properties.homomorphisms import count_homomorphisms




def aggregate_quotient_coefficients(graphlets):
    """
    Aggregate quotient coefficients by isomorphism type.

    The input graphlets are assumed to be exactly the graphlets satisfying Phi and up to a certain arity.

    For every graphlet H and every partition rho of V(H), we compute H/rho.
    Quotients that are isomorphic are merged into the same coefficient.
    """
    representatives = []
    coefficients = {}

    for H in graphlets:
        aut_count = len(hypergraph_automorphisms(H))

        for partition in vertex_partitions(H.vertices):
            quotient = H.quotient(partition)
            mu = moebius_function(partition)

            representative = find_isomorphic_representative(quotient, representatives)

            if representative is None:
                representative = quotient
                representatives.append(representative)
                coefficients[representative] = Fraction(0, 1)

            coefficients[representative] += Fraction(mu, aut_count)

    return coefficients

def count_edge_subgraphs_via_formula(graphlets, G):
    """
    Evaluate formula (6), after aggregating quotients by isomorphism type.

    Every H in graphlets is assumed to satisfy the desired property.
    """
    coefficients = aggregate_quotient_coefficients(graphlets)
    total = Fraction(0, 1)

    for F, coefficient in coefficients.items():
        hom_count = count_homomorphisms(F, G)
        total += coefficient * hom_count

    return total

def print_quotient_coefficients(graphlets):
    """
    Print the aggregated quotient coefficients.

    Useful for checking that the quotient aggregation behaves as expected.
    """
    coefficients = aggregate_quotient_coefficients(graphlets)

    for i, F in enumerate(coefficients):
        print("Quotient type", i)
        print(F)
        print("Coefficient:", coefficients[F])
        print()