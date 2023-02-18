"""Test the computation of probabilities and correlations."""

from __future__ import print_function, division, unicode_literals

from cudd import Cudd

mgr = Cudd()

n = 3
a,b,c = (mgr.bddVar(i, chr(ord('a') + i)) for i in range(n))

f = a & (~b | c)
print('f =', f)
f.summary(name='f')
f.display(name='f')
print(f.essential())
print(f.probabilities())
print('correlation =', [f.correlation(v) for v in [a,b,c]])
