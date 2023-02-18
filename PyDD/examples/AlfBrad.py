"""A knights and knaves puzzle by Smullyan.

   What statement uttered by both Alfred and Bradford allows one to conclude
   that their sister is not married?

   Note that since both brothers make the same statement, they must be both
   knights or both knaves.
"""

from __future__ import print_function

def convert(x):
    return "-" if x == 2 else str(x)

def list_to_string(prime):
    return "".join(map(convert, prime))

def list_to_cube(prime):
    ret = mgr.bddOne()
    for i in range(len(prime)):
        if prime[i] == 1:
            ret &= mgr.bddVar(i)
        elif prime[i] == 0:
            ret &= ~mgr.bddVar(i)
    return ret

from cudd import Cudd
mgr = Cudd()

stmt = mgr.bddVar(0, 'stmt') # equation's unknown
ta = mgr.bddVar(1, 'ta')     # Alfred is truthful
tb = mgr.bddVar(2, 'tb')     # Bradford is truthful
sm = mgr.bddVar(3, 'sm')     # their sister is married

# We solve a Boolean equation F = 0, which says that the brothers' statement
# is a function of ta, tb, and sm and moreover that
# (ta <-> stmt) and (tb <-> stmt) implies ~sm.
F = ta.iff(stmt) & tb.iff(stmt) & sm

# Let's find the most general solution.
(consist, solutions) = F.solveEqn([stmt], True)

if consist.isZero():
    print("Equation is unconditionally consistent")
else:
    print("Consistency condition:", consist)
print("General solution:")
solutions[0].printCover()

# We compute the particular solution with the parameter set to ~(ta & tb & sm).
# This function is indeed a solution; hence we get it back by substituting it
# for the parameter.
particular = solutions[0].compose(~(ta & tb & sm), stmt.index())
print("Particular solution:", particular)

another = solutions[0].compose(~sm, stmt.index())
print("Another solution   :", another)

# We enumerate a prime cover of the interval defined by the general solution.
# This produces an invalid solution because Bradford contradicts himself.
lower = solutions[0].cofactor(~stmt)
upper = solutions[0].cofactor(stmt)
cover = mgr.bddZero()
for prime in lower.generate_primes(upper):
    cover |= list_to_cube(prime)
# If the following test fails, the antecedent of the implication is vacuous.
if (cover.iff(ta) & cover.iff(tb)):
    cover.printCover()
    print(cover)
