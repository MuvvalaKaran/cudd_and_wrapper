"""Example of solution of Boolean equation."""

from __future__ import print_function
from cudd import Cudd
m = Cudd()

# Unknowns and independent variables.
names = ['A', 'B', 'C', 'D']
n = len(names)
A,B,C,D = (m.bddVar(i, names[i]) for i in range(n))

# Build LHS of equation F(D,A,B,C) = 0.
K = (~A | ~B | C) & (~C | A)
F = ~(~K | ((~B | D) & C.iff(A & D)))
print("F =", F)

# Solve equation (and verify solution).
(consist, solutions) = F.solveEqn([D],True)

if consist.isZero():
    print("Equation is unconditionally consistent")
else:
    print("Consistency condition:", consist)
print("Solution:")
print(solutions[0])
solutions[0].printCover()
print(solutions[0].cofactor(~D), ' | p & (', solutions[0].cofactor(D),
      ')', sep='')

# Compute the particular solution with the parameter set to "true."
p = solutions[0]
p = p.compose(m.bddOne(), D.index())
print("Particular solution for p = true  :", p)

# Compute the particular solution with the parameter set to C.
p = solutions[0]
p = p.compose(C, D.index())
print("Particular solution for p = C     :", p)

# Compute the particular solution with the parameter set to B | C.
p = solutions[0]
p = p.compose(B | C, D.index())
print("Particular solution for p = B | C :", p)
