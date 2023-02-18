"""
Check van der Waerden numbers W(r,r).  That is, van der Waerden numbers
for runs of two colors of the same length.
"""

from __future__ import print_function, unicode_literals, division
import argparse
from cudd import Cudd

def constraint(r,i,s):
    """Compute constraint for given run length, starting index and step."""
    rv = mgr.bddZero()
    for j in range(1,r):
        rv |= x[i] ^ x[i+j*s]
    if args.verbose > 1:
        rv.summary(name='rv')
        rv.printCover()
    return rv

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve tournament puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-a", "--apa", help="use arbitrary precision arithmetic",
                    action="store_true", default=False)
parser.add_argument("-n", "--number", help="number to be tested",
                    type=int, default=8)
parser.add_argument("-r", "--run", help="length of run",
                    type=int, default=3)
parser.add_argument("-m", "--memory", help="target maximum memory",
                    type=int, default=8000000000)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)

args = parser.parse_args()

if args.verbose > 0:
    print([(arg, getattr(args, arg)) for arg in vars(args)])

n = args.number
run = args.run

mgr = Cudd(bddVars=n, maxMem=args.memory)

x = [mgr.bddVar(i, 'x%d' % i) for i in range(n)]

w = x[-1] # Symmetry reduction
for m in range(run,n+1):
    for length in range(run, m+1, run-1):
        step = (length - 1) // (run -1)
        w &= constraint(run,n-m,step)
    if args.apa: w.summary(name='w%d' % m, numVars=m)
    else: w.display(name='w%d' % m, detail=1, numVars=m)

w.summary(name='final')
if args.verbose > 0: w.printCover()
