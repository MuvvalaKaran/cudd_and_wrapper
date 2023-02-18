"""N-queens problem."""

from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse
from math import ceil, log
from random import sample
from cudd import Cudd, REORDER_GROUP_SIFT_CONV

def check_positive_number(value):
    """Check that the argument is a positive integer."""
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            "%s is not a positive integer" % value)
    return ivalue

class Cache:
    """
    Implements a cache for constraint building blocks that
    are repeatedly needed in the sampling approach.
    """
    def __init__(self, N):
        self.bounds = [None for _ in range(N)]
        self.noattack = [[None for j in range(N)] for i in range(N)]

    def put_bound(self, i, b):
        self.bounds[i] = b

    def get_bound(self, i):
        return self.bounds[i]

    def put_noattack(self, i, j, b):
        self.noattack[i][j] = b

    def get_noattack(self, i, j):
        return self.noattack[i][j]

def reduce_list(lst):
    """Destructively reduce a list of BDDs to their conjunction."""
    while len(lst) > 1:
        if args.verbose > 0:
            for b in lst:
                b.summary()
            print('*' * 10)
        j = 0
        for i in range(0,len(lst)-1,2):
            lst[j] = lst[i] & lst[i+1]
            j += 1
        if len(lst) % 2 == 1:
            lst[j] = lst[-1]
            j += 1
        del lst[j:]

def build_constraints(constraints=None, cache=None):
    """Build the BDD for the queen placements."""
    if constraints is None:
        constraints = m.bddOne()

    lst = []

    if cache is None:
        if args.reduction:
            b = m.interval(Q[0],0,(N-1)//2)
        else:
            b = m.interval(Q[0],0,N-1)
    else:
        b = cache.get_bound(0)
        if b is None:
            if args.reduction:
                b = m.interval(Q[0],0,(N-1)//2)
            else:
                b = m.interval(Q[0],0,N-1)
            cache.put_bound(0, b)
    lst.append(constraints & b)

    for i in range(1,N):
        if cache is None:
            b = m.interval(Q[i],0,N-1)
        else:
            b = cache.get_bound(i)
            if b is None:
                b = m.interval(Q[i],0,N-1)
                cache.put_bound(i, b)
        lst.append(constraints & b)

    if args.reduction:
        lst.append(constraints & m.inequality(0, Q[N-1], Q[0]))

    for i in range(N-1):
        for j in range(i+1,N):
            if cache is None:
                b = (~m.xeqy(Q[i],Q[j]) &
                     m.disequality(j-i, Q[i], Q[j]) &
                     m.disequality(j-i, Q[j], Q[i]))
            else:
                b = cache.get_noattack(i, j)
                if b is None:
                    b = (~m.xeqy(Q[i],Q[j]) &
                         m.disequality(j-i, Q[i], Q[j]) &
                         m.disequality(j-i, Q[j], Q[i]))
                    cache.put_noattack(i, j, b)
            lst.append(constraints & b)

    reduce_list(lst)
    lst[0].summary(name='constraints')
    return lst[0]

def random_cuts(ncuts, nvars):
    """Build ncuts constraints, each with nvars randomly chosen variables."""
    cuts = []
    for c in range(ncuts):
        pairs = [(x // bits, x % bits) for x in sample(range(N*bits), nvars)]
        vars = [Q[i][j] for (i,j) in pairs]
        cut = reduce(lambda a, b: a ^ b, vars)
        cuts.append(cut)
    return cuts

def print_report():
    """Print solutions."""
    if args.verbose > 0:
        for model in constraints.generate_cubes():
            if len(model) != N*bits:
                raise ValueError('Wrong number of variables in model')

            qp = [int(''.join((str(x) for x in model[i*bits:(i+1)*bits])), 2)
                  for i in range(N)]
            if args.verbose > 1:
                matrix = [['   |' for j in range(N)] for i in range(N)]
                separ = "+---" * N + "+"
                print(separ)
                for i in range(N):
                    matrix[i][qp[i]] = ' ' + str(qp[i]) + ' |'
                    print("|", "".join(matrix[i]), sep="")
                    print(separ)
            else:
                print(qp)

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
parser.add_argument("-s", "--sample", help="use sampling", action="store_true")
parser.add_argument("--reorder", help="reorder BDD variables",
                    action="store_true")
parser.add_argument("--stats", help="print BDD stats", action="store_true")
parser.add_argument("-m", "--memory", help="target maximum memory",
                    type=check_positive_number, default=0)
args = parser.parse_args()

N = args.number
bits = int(ceil(log(N,2)))

m = Cudd(bddVars=N*bits, maxMem=args.memory)

# Standard encoding: for each row, track the column occupied by the queen.
Q = [[m.bddVar(i*bits+b, 'Q_%s_%s' % (i, b)) for b in range(bits)]
     for i in range(N)]

if args.verbose > 0: print('Number of variables = ', m.size())

if args.sample:
    samples = 30
    cuts = random_cuts(3*bits, 3)
    count = 0
    for i in sample(range(2**len(cuts)), samples):
    #for i in range(2**len(cuts)):
        v = i
        b = m.bddOne()
        for j in range(len(cuts)):
            b &= cuts[j] if v % 2 else ~cuts[j]
            v //= 2
        print(i, end='')
        cache = Cache(N)
        b = build_constraints(b, cache)
        count += b.count()
    #print('count =', count)
    print('estimate =', count * 2**len(cuts) / samples)
else:    
    constraints = build_constraints()
    print_report()
    if args.reorder:
        m.enableReorderingReporting()
        for i in range(N):
            m.makeTreeNode(i*bits, bits)
        m.reduceHeap(REORDER_GROUP_SIFT_CONV)
        m.printBddOrder()

if args.stats:
    m.printInfo()
