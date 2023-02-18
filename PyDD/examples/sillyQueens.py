"""N-queens problem with silly encoding and priority queue."""

from __future__ import print_function, division, unicode_literals
from heapq import heapify, heappush, heappop
import argparse
from cudd import Cudd, REORDER_SIFT_CONVERGE

def check_positive_number(value):
    """Check that the argument is a positive integer."""
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            "%s is not a positive integer" % value)
    return ivalue

def reduce_list(lst):
    """Use priority queue to always conjoin smallest BDDs."""
    h = [(b.size(), b) for b in lst]
    heapify(h)
    del lst[1:]

    while len(h) > 1:
        c = heappop(h)[1] & heappop(h)[1]
        sc = c.count()
        if args.verbose > 0:
            print(len(h), c.size())
        heappush(h, (sc,c))
    lst[0] = heappop(h)[1]

def build_constraints(constraints=None, cache=None):
    """Build the BDD for the queen placements."""

    lst = [m.cardinality(Q[i],1) for i in range(N)]

    if args.reduction:
        lst.append(m.cardinality(Q[0][0:N//2],0))
        if N % 2 == 1:
            lst.append(~Q[0][N//2] | m.cardinality(Q[1][0:N//2],0))

    for j in range(N):
        lst.append(m.cardinality([Q[i][j] for i in range(N)],1))

    for d in range(N):
        lst.append(m.cardinality([Q[i][d+i] for i in range(N-d)],0,1))
        lst.append(m.cardinality([Q[d+i][i] for i in range(N-d)],0,1))
        lst.append(m.cardinality([Q[i][N-1-d-i] for i in range(N-d)],0,1))
        lst.append(m.cardinality([Q[d+i][N-1-i] for i in range(N-d)],0,1))

    reduce_list(lst)
    return lst[0]

def print_report():
    """Print solutions."""
    if args.verbose > 0:
        for model in constraints.generate_cubes():
            if len(model) != N*N:
                raise ValueError('Wrong number of variables in model')

            if args.verbose > 1:
                separ = "+---" * N + "+"
                print(separ)
                for i in range(N):
                    line = [' ' + str(model[i*N+j]) + ' |' for j in range(N)]
                    print("|", "".join(line), sep="")
                    print(separ)
            else:
                print(' '.join([str(x) for x in model]))

            if args.verbose < 3:
                break


# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve the N-queens problem",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--number", help="number of queens (> 0)",
                    type=check_positive_number, default=4)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
parser.add_argument("-r", "--reduction", help="apply symmetry reduction",
                    action="store_true")
parser.add_argument("--reorder", help="reorder BDD variables",
                    action="store_true")
parser.add_argument("--stats", help="print BDD stats", action="store_true")
parser.add_argument("-m", "--memory", help="target maximum memory",
                    type=check_positive_number, default=8000000000)
args = parser.parse_args()

N = args.number

m = Cudd(bddVars=N*N, maxMem=args.memory)

# Standard encoding: for each row, track the column occupied by the queen.
Q = [[m.bddVar(i*N+c, 'Q_%s_%s' % (i, c)) for c in range(N)]
     for i in range(N)]

if args.verbose > 0: print('Number of variables = ', m.size())

constraints = build_constraints()
constraints.summary(name="constraints")
print_report()

if args.reorder:
    m.enableReorderingReporting()
    m.reduceHeap(REORDER_SIFT_CONVERGE)
    m.printBddOrder()

if args.stats:
    m.printInfo()
