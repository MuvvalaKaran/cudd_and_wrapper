""" Reliability polynomial example from Knuth's Fascicle 5a. 

    Given a prime cover of a monotone Boolean function f, let X be
    the number of prime implicants of f that are true for a given 
    variable assignment.  For given probabilities of the variables in f,
    we compute Pr(X > 0) in two different ways.  We also compute
    two approximations to it.
"""

from __future__ import print_function
from cudd import Cudd

mgr = Cudd()

N = 5
x1,x2,x3,x4,x5 = [mgr.bddVar(i, 'x%s' % (i+1)) for i in range(N)]
# Impose an optimal variable order.  This leads to printing a nicer formula.
mgr.shuffleHeap([v.index() for v in [x4, x5, x1, x2, x3]])

implicants = [x1 & x2 & x3, x2 & x3 & x4, x4 & x5]
f = implicants[0] | implicants[1] | implicants[2]
p = [0.9] * N
print('f =', f)
f.printCover()

print('Pr(X > 0) for p =', p)

# Check whether the cover of f is monotone, prime, and irredundant.
for imp in implicants:
    if not imp.isPositive():
        raise RuntimeError('%s is not monotone' % imp.cubeString())
# Check whether the cover is prime and irredundant by checking for
# duplicates.  We rely on the fact that BDD objects are hashable.
# We also rely on the fact that every implicant of a unate cover
# either is subsumed by another implicant, or is an essential prime.
if len(implicants) != len(set(implicants)):
    raise RuntimeError('the given cover of f is not irredundant')

# Compute Pr(X > 0) as the probability that f is true.
print('BDD value =', f.probability(p))

# Compute the same value from the DNF.  This process is rather laborious,
# but it doesn't build the BDD for f; it only builds the BDD for the
# disjunction of the conjunctions of each prime and the previous primes
# (for an arbitrary, fixed order).  Moreover, it only directly computes
# the probabilities of cubes.
dnfval = implicants[0].probability(p)
for i in range(1,len(implicants)):
    dnfval += implicants[i].probability(p)
    disjunction = mgr.bddZero()
    for j in range(i):
        disjunction |= implicants[i] & implicants[j]
    for c in disjunction.generate_cubes():
        dnfval -= disjunction.probability(p)

print('DNF value =', dnfval)

# Apply Ross's conditional expectation inequality.
ceiBound = 0
for imp in implicants:
    numerator = imp.probability(p)
    denominator = sum((c.constrain(imp).probability(p) for c in implicants))
    ceiBound += numerator / denominator

print('bound from conditional expectation inequality =', ceiBound)

# Apply the second moment principle.

# Split f into disjoint cubes such that the minterms of each cube are
# all covered by the same implicants. (Here we rely on the fact that
# generate_cubes enumerates a disjoint cover.)

def split_cube(cube, cover):
    """Split cube into cubes whose minterms are all covered by the same cubes."""
    if not cover:
        return [cube]
    car,cdr = (cover[0],cover[1:])
    conjunction = car & cube
    if not cube <= car and conjunction:
        splits = split_cube(conjunction, cdr)
        for c in (cube & ~car).generate_cubes():
            splits += split_cube(mgr.fromLiteralList(c), cdr)
    else:
        splits = split_cube(cube, cdr)
    return splits

splits = []
for cube in f.generate_cubes():
    splits += split_cube(mgr.fromLiteralList(cube), implicants)

# Compute the expected values of X and X squared.
EX = EX2 = 0
for cube in splits:
    val = sum((cube <= imp for imp in implicants))
    prob = cube.probability(p)
    EX += val * prob
    EX2 += val**2 * prob
    print('  X(%s) = %d, p = %f' % (cube.cubeString(), val, prob))

print('bound from second moment principle =', EX**2 / EX2)
