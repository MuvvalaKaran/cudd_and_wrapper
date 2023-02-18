"""Count knight's tours (both open and closed).

   Only practical for NxN boards with N < 6.
"""

from __future__ import print_function, division, unicode_literals
import argparse
from math import ceil, log
from cudd import Cudd, REORDER_GROUP_SIFT_CONV

def check_positive_number(value):
    """Check that the argument is a positive integer."""
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            "%s is not a positive integer" % value)
    return ivalue

def valid_move(i):
    """Constrain move to that of a knight."""
    return (
        (((m.interval(C[i],0,N-2) & ~m.disequality(1,C[i+1],C[i]))
          | (m.interval(C[i],1,N-1) & ~m.disequality(1,C[i],C[i+1])))
         &
         ((m.interval(R[i],0,N-3) & ~m.disequality(2,R[i+1],R[i]))
          | (m.interval(R[i],2,N-1) & ~m.disequality(2,R[i],R[i+1]))))
        |
        (((m.interval(C[i],0,N-3) & ~m.disequality(2,C[i+1],C[i]))
          | (m.interval(C[i],2,N-1) & ~m.disequality(2,C[i],C[i+1])))
         &
         ((m.interval(R[i],0,N-2) & ~m.disequality(1,R[i+1],R[i]))
          | (m.interval(R[i],1,N-1) & ~m.disequality(1,R[i],R[i+1]))))
    )

# Parse command line.
parser = argparse.ArgumentParser(
    description="Count knight's tours",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--side", help="length of board side (> 0)",
                    type=check_positive_number, default=4)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
#parser.add_argument("-r", "--reduction", help="apply symmetry reduction",
#                    action="store_true")
parser.add_argument("--reorder", help="reorder BDD variables",
                    action="store_true")
parser.add_argument("--stride", help="use increasing stride strategy",
                    action="store_true")
parser.add_argument("--stats", help="print BDD stats", action="store_true")
parser.add_argument("-m", "--memory", help="target maximum memory",
                    type=check_positive_number, default=0)
args = parser.parse_args()

N = args.side
bits = int(ceil(log(N,2)))

m = Cudd(bddVars=N*bits, maxMem=args.memory)

# Row and column variables.  Each position in the tour is given by
# a row number and a column number.
R = [[m.bddVar(2*i*bits+b, 'R_%s_%s' % (i, b)) for b in range(bits)]
     for i in range(N*N)]
C = [[m.bddVar((2*i+1)*bits+b, 'C_%s_%s' % (i, b)) for b in range(bits)]
     for i in range(N*N)]

if args.verbose > 0:
    print('Number of variables = ', m.size())
    if args.verbose > 1:
        print('order:', ' '.join(m.bddOrder()))

F = m.bddOne()

# For odd N, this ignores the tours starting at the center of the board.
#if args.reduction:
#    F &= m.interval(R[0],0,(N-2)//2) & m.interval(C[0],0,(N-1)//2)

# Impose knight's moves.
for i in range(N*N-1):
    F &= valid_move(i)

# Impose the distinctness constraint.
if args.stride:
    for stride in range(2,N*N,2):
        if args.verbose > 0:
            F.display(detail=1,name='F'+str(stride))
        for i in range(N*N-stride):
            j = i + stride
            F &= ~(m.xeqy(R[i],R[j]) & m.xeqy(C[i],C[j]))
else:
    for i in range(N*N-3,-1,-1):
        if args.verbose > 0:
            F.display(detail=1,name='F'+str(i))
        diff = m.bddOne()
        for j in range(i+2,N*N,2):
            diff &= ~(m.xeqy(R[i],R[j]) & m.xeqy(C[i],C[j]))
        F &= diff

if args.verbose > 1:
    F.display(name='F')
else:
    F.summary(name='F')

if args.reorder:
    m.enableReorderingReporting()
    for i in range(N*N):
        m.makeTreeNode(i*bits, bits)
    m.reduceHeap(REORDER_GROUP_SIFT_CONV)
    print('order:', ' '.join(m.bddOrder()))

if args.stats:
    m.printInfo()
