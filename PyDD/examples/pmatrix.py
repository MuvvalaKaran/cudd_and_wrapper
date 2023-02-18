"""
Compute cosets of a parity-check code from their parity-check matrix
and a corrector/syndrome.  For the all-zero corrector, we get the set
of codewords.

The parity-check matrix is

 [ 1 1 1 0 0 0 ]
 [ 1 0 1 1 0 1 ]
 [ 0 1 1 0 1 1 ]

which has rank 3.  Hence there are 8 codewords.

A minimum-distance decoder can be based on these coset leaders:

000 000000
001 000010
010 000100
011 000001
100 001001
101 010000
110 100000
111 001000
"""
from __future__ import print_function, unicode_literals, division
from cudd import Cudd

def unpack(n):
    u = []
    for i in range(3):
        u = [n % 2] + u
        n //= 2
    return u

n = 6

mgr = Cudd(bddVars=n)

x = [mgr.bddVar(i, 'x%d' % i) for i in range(n)]

for i in range(8):
    corrector = unpack(i)
    c = [mgr.bddZero() if i == 0 else mgr.bddOne() for i in corrector]

    f = (c[0].iff(x[0] ^ x[1] ^ x[2]                     ) &
         c[1].iff(x[0]        ^ x[2] ^ x[3]        ^ x[5]) &
         c[2].iff(       x[1] ^ x[2]        ^ x[4] ^ x[5]))

    print('corrector =', ''.join([str(i) for i in corrector]))
    f.printCover()
