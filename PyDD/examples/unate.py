""" Test functions about primes and unate functions."""

from __future__ import print_function

from cudd import Cudd

mgr = Cudd()

n = 4
a,b,c,d = (mgr.bddVar(i, chr(ord('a') + i)) for i in range(n))

f = (a & b | b & c) & ~d
print('f:', f)

for i in range(n):
    print("f is decreasing in", mgr.bddVar(i), ":", f.isDecreasing(i))
    print("f is increasing in", mgr.bddVar(i), ":", f.isIncreasing(i))

c = a & b & ~c & ~d

p = c.makePrime(f)
print('prime:', p)

try:
    # trying to expand a non-cube
    print('try', (a|b).makePrime(f))
except MemoryError as e:
    print('what happened:', e)

me = c.maximallyExpand(mgr.bddOne(), f)
print('maximal expansion:', me)
print('e and f are the same:', me == f)

try:
    # non-cube BDD
    print('try', (a|b).maximallyExpand(mgr.bddOne(), f))
except MemoryError as e:
    print('what happened:', e)

try:
    # upper bound too small
    print('try', c.maximallyExpand(mgr.bddZero(), f))
except MemoryError as e:
    print('what happened:', e)

u = f.largestPrimeUnate(a&b&c&~d)
print('unate', u)

try:
    # wrong unateness cube
    u2 = f.largestPrimeUnate(a&~b&c&~d)
except MemoryError as e:
    print('what happened:', e)

try:
    # non-cube argument
    u3 = f.largestPrimeUnate(a|b&c&~d)
except MemoryError as e:
    print('what happened:', e)
