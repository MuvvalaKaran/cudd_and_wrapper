"""Test of ADD matrix operations."""

from __future__ import print_function
from cudd import Cudd, RESIDUE_MSB
m = Cudd()

n = 2
x = [m.addVar(i*3,   'x' + str(i)) for i in range(n)]
y = [m.addVar(i*3+1, 'y' + str(i)) for i in range(n)]
z = [m.addVar(i*3+2, 'z' + str(i)) for i in range(n)]

print("Walsh")
W1 = m.Walsh(x, z)
W1.display(2*n)
W2 = m.Walsh(z, y)
W2.display(2*n)

prod = W1.matrixMultiply(W2, z)
prod.display(2*n)

print(prod.bddPattern())
print((m.xeqy(x, y) * m.addConst(2**n)) == prod)

print("Hamming")
m.Hamming(x, y).display(2*n)

print("Residues")
m.residue(3*n, 3).display(3*n)
m.residue(2*n, 3, RESIDUE_MSB).display(2*n)

print("Gauss-Jacobi")
c0,c1,c3,c4,c5,c6,c10 = (m.addConst(r) for r in [0.0,1.0,3.0,4.0,5.0,6.0,10.0])
# A is diagonally dominant.
A = x[0].ite(x[1].ite(z[0].ite(z[1].ite(c1, c0), c0),
                      z[0].ite(z[1].ite(c0, c6),z[1].ite(-c4, c1))),
             x[1].ite(z[0].ite(z[1].ite(c0, c1),z[1].ite(-c4, c1)),
                      z[0].ite(z[1].ite(c0, c4),z[1].ite(-c4, c10))))
A.display(2*n)

b = x[0].ite(x[1].ite(c1, c10),x[1].ite(c5, -c3))
b.display(n)

I = m.xeqy(x, z)
diag = I.ite(A, c0)
zcube = c1
for i in range(n):
    zcube &= z[i]
D = diag.existAbstract(zcube)
R = I.ite(c0, A)
u = c0

for i in range(100):
    oldu = u
    uz = u.swapVariables(x, z)
    u = (b - R.matrixMultiply(uz, z)) / D
    if u.equalSupNorm(oldu, 1e-12):
        print("converged after", i, "iterations")
        break

print(u)
