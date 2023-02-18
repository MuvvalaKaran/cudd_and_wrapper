"""Test NP and."""

from __future__ import print_function, division, unicode_literals

from cudd import Cudd

def show(f, name):
    """Show function."""
    f.summary(name=name)
    f.printCover()

mgr = Cudd()

n = 4
a,b,c,d = (mgr.bddVar(i, chr(ord('a') + i)) for i in range(n))

f1 = d.iff(c).iff(b).iff(a)
show(f1,'f1')

g1 = (d & c & b & a) | ~(d | c | b | a)
show(g1,'g1')

h1 = f1.npAnd(g1)
show(h1,'h1')

assert(h1 == g1.npAnd(f1))

f2 = c.iff(b).iff(a)
show(f2,'f2')

g2 = mgr.cardinality([a,b,c], 1)
show(g2,'g2')

h2 = f2.npAnd(g2)
show(h2,'h2')

assert(h2 == g2.npAnd(f2))

f3 = (b & a) | (c ^ d)
show(f3,'f3')

g3 = d  | (c & ~b & ~a)
show(g3,'g3')

h3 = f3.npAnd(g3)
show(h3,'h3')
print(h3)

