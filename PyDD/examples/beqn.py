"""Example of solution of Boolean equation."""

from __future__ import print_function
from cudd import Cudd
m = Cudd()

# Unknowns and independent variables.
n = 3
y = [m.bddVar(i, 'y' + str(i)) for i in range(n)]
x = m.bddVar(n, 'x')

# Build LHS of equation F(y,x) = 0.
F = ((y[0] | y[2]) & y[1]) | ((~y[0] | ~y[2]) & ~x)
print("F =", F)

# Solve equation (and verify solution).
(consist, solutions) = F.solveEqn(y,True)

if consist.isZero():
    print("Equation is unconditionally consistent")
else:
    print("Consistency condition:", consist)
print("Solutions:")
for g in solutions:
    print(g)

# Compute the particular solution with all parameters set to "true."
print("Particular solution:")
for g in solutions:
    p = g
    for u in y:
        p = p.compose(m.bddOne(), u.index())
    print(p)
