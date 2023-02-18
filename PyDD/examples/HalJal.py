"""A knights and knaves puzzle by Smullyan.

   What statement uttered by Hal allows one to conclude that
   Hal and Jal are either both knights or both knaves?
"""

from __future__ import print_function

def convert(x):
    return "-" if x == 2 else str(x)

def list_to_string(prime):
    return "".join(map(convert, prime))

from cudd import Cudd
mgr = Cudd()

stmt = mgr.bddVar(0, 'stmt') # Equation unknown
th = mgr.bddVar(1, 'th')     # Hal is truthful
tj = mgr.bddVar(2, 'tj')     # Jal is truthful

# We solve a Boolean equation F = 0, which says that Hal's statement is a
# function of th and tj and moreover (th <-> stmt) if and only if (th <-> tj).
F = th.iff(stmt) ^ th.iff(tj)

# From F above it's pretty obvious that stmt=tj is a solution of F = 0.
# Let's be systematic, though, and find the most general solution.
(consist, solutions) = F.solveEqn([stmt], True)

if consist.isZero():
    print("Equation is unconditionally consistent")
else:
    print("Consistency condition:", consist)
print("General solution:")
solutions[0].printCover()

# We compute the particular solution with the parameter set to tj.
# If tj is indeed a solution, we get it by substituting it for the parameter.
particular = solutions[0].compose(tj, stmt.index())
print("Particular solution:", particular)

# We enumerate a prime cover of the interval defined by the general solution.
lower = solutions[0].cofactor(~stmt)
upper = solutions[0].cofactor(stmt)
print('Interval:')
for prime in lower.generate_primes(upper):
    print(list_to_string(prime))
