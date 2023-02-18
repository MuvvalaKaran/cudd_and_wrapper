"""Test of ZDD-based weak division."""

from __future__ import print_function

from cudd import Cudd

m = Cudd()
n = 5
a,b,c,d,e = (m.bddVar(i, 'x' + str(i)) for i in range(n))
m.zddVarsFromBddVars(2)

f = a&b&(c|d) | (b|c|d)&e
f.display(name="f")

(dummy,fc) = f.isop(f, True)

print("f cover:")
fc.printCover()

g = a&b | e

(dummy,gc) = g.isop(g, True)
print("g cover:")
gc.printCover()

qc = fc.weakDiv(gc)
print("quotient cover:")
qc.printCover()

pc = gc.product(qc)
print("gq cover:")
pc.printCover()

rc = fc.diff(pc)
print("remainder cover:")
rc.printCover()

print("equivalence is preserved:", fc == pc | rc)
