""" Solve this puzzle: A list of n claims is given.  

    (a) The i-th claim is: Exactly i of these n claims are false.
    (b) The i-th claim is: At least i of these n claims are false.

    What do we know in each case?
"""

from __future__ import print_function, unicode_literals, division
import argparse
from cudd import Cudd

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve puzzle of list of claims",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--number", help="number of claims",
                    type=int, default=100)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)

args = parser.parse_args()
n = args.number

mgr = Cudd()

claim = [mgr.bddVar(i, 'c%d' % i) for i in range(n)]

f = g = mgr.bddOne()
for i in range((n+1) // 2):
    f &= claim[i].iff(mgr.cardinality(claim,n-i-1))
    g &= claim[i].iff(mgr.cardinality(claim,0,n-i-1))
    f &= claim[n-i-1].iff(mgr.cardinality(claim,i))
    g &= claim[n-i-1].iff(mgr.cardinality(claim,0,i))
    if args.verbose > 1:
        print('f essential', end=''), f.essential().display()
        print('g essential', end=''), g.essential().display()

print('f', end=''), f.display()
print('g', end=''), g.display()
