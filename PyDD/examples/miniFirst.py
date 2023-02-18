"""Test minimization algorithms."""

from __future__ import print_function, division, unicode_literals

from cudd import Cudd

def show(f, name):
    """Show function."""
    f.summary(name=name)
    f.printCover()

m = Cudd()

n = 4
a,b,c,d = (m.bddVar(i, chr(ord('a') + i)) for i in range(n))

first = ~((~c & d) | (~b & ~d) | (~b & c & d) | (a & ~c & ~d) | (~a & b & ~d))
show(first,'first')

second = (~a & ~b & ~c) | (b & c) | (a & ~b & c)
show(second,'second')

lb = first & second
show(lb,'lb')

ub = first | ~second
show(ub,'ub')

print('optimal cover')
lb.printCover(ub)

npa = first.npAnd(second)
show(npa,'npa')
assert(lb <= npa <= ub)

kmap = b & (a | d)
show(kmap,'kmap')
assert(lb <= kmap <= ub)

mini = first.minimize(second)
show(mini,'mini')

#m.dumpDot([first, second, npa], ['f', 's', 'n'], file_path='npa.dot')

m.shuffleHeap([v.index() for v in [b,c,a,d]])
print('new order: ', end='')
m.printBddOrder()

show(first,'first')
show(second,'second')
npa2 = first.npAnd(second)
show(npa2,'npa2')

