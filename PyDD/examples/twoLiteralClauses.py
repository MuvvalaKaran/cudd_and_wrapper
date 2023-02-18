"""Test two-literal clauses functions."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()

a,b,c,d = (m.bddVar(i, chr(ord('a') + i)) for i in range(4))

f = (a | c) & (~a | ~c) & (b | d) & (~b | ~d)
print("f =", f)
f.printTwoLiteralClauses()

ff = m.bddOne()
for c in f.twoLiteralClauses():
    print(c)
    ff &= c
if f != ff:
    raise RuntimeError()

g = a & (b | c & d)
print("\ng =", g)
g.printTwoLiteralClauses()

gg = m.bddOne()
for c in g.twoLiteralClauses():
    print(c)
    gg &= c
if g != gg:
    raise RuntimeError()

