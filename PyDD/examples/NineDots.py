"""Number of possibly intersecting paths on a 3x3 grid of
   lengths at least 4.  Knight's moves are allowed.
"""
from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse

def reportC(title):
    """Print summary of solutions."""
    if args.verbose > 1:
        C.display(numVars=n*m, name=title)
    elif args.verbose > 0:
        C.summary(numVars=n*m, name=title)

def print_solutions(solutions):
    """Convert BDD to list of solutions."""
    count = args.number
    if not count is None:
        if count > 1:
            print ('First', count, 'solutions')
        elif count > 0:
            print ('First solution')
    while not solutions.isZero():
        if not count is None:
            if count == 0:
                return
            count -= 1
        soln = solutions.pickOneMinterm()
        solutions &= ~soln
        cube = soln.pickOneCube()          # convert to list of 0s and 1s
        pint = [None] * n
        for i in range(n):
            pint[i] = int(''.join(map(str, cube[m*i:m*(i+1)])),2)
        print(' '.join([str(x) for x in pint if x != 0]))

def hasValue(index, value, other=None):
    return mgr.interval(p[index], value, other)

def alreadySeen(before, value):
    rv = mgr.bddZero()
    for i in range(before):
        rv |= hasValue(i, value)
    return rv

# Parse command line.
parser = argparse.ArgumentParser(
    description='Count cell phone lock patterns',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='count', default=0)
parser.add_argument('-n', '--number', help='maximum number of solutions to be printed',
                    type=int, default=None)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = 9 # number of numbers
m = 4 # number of bits in each number

# p[i] gives the dot at the i-th step of the path, or 0 is there is
# no such step.
p = [[mgr.bddVar(m*i+j, 'p_' + str(i) + '_' + str(j)) for j in range(m)]
     for i in range(n)]

C = mgr.bddOne()

# Every dot number is between 0 (past the end of the sequence) and 9.
# The first four numbers must be strictly positive.
# If a number is in the sequence (different from 0) it must be
# unique; otherwise, all its successors must be 0.
for i in range(n):
    if i > 3:
        C &= mgr.interval(p[i],0,9)
    else:
        C &= mgr.interval(p[i],1,9)
    for j in range(i+1,n):
        C &= hasValue(i,0).ite(hasValue(j,0), ~mgr.xeqy(p[i],p[j]))

reportC('before adjacency')

for i in range(n-1):
    C &= ~hasValue(i,1) | ((~hasValue(i+1,3) | alreadySeen(i,2)) &
                           (~hasValue(i+1,7) | alreadySeen(i,4)) &
                           (~hasValue(i+1,9) | alreadySeen(i,5)))
    C &= ~hasValue(i,2) | (~hasValue(i+1,8) | alreadySeen(i,5))
    C &= ~hasValue(i,3) | ((~hasValue(i+1,1) | alreadySeen(i,2)) &
                           (~hasValue(i+1,9) | alreadySeen(i,6)) &
                           (~hasValue(i+1,7) | alreadySeen(i,5)))
    C &= ~hasValue(i,4) | (~hasValue(i+1,6) | alreadySeen(i,5))
    C &= ~hasValue(i,6) | (~hasValue(i+1,4) | alreadySeen(i,5))
    C &= ~hasValue(i,7) | ((~hasValue(i+1,1) | alreadySeen(i,4)) &
                           (~hasValue(i+1,9) | alreadySeen(i,8)) &
                           (~hasValue(i+1,3) | alreadySeen(i,5)))
    C &= ~hasValue(i,8) | ( ~hasValue(i+1,2) | alreadySeen(i,5))
    C &= ~hasValue(i,9) | ((~hasValue(i+1,7) | alreadySeen(i,8)) &
                           (~hasValue(i+1,3) | alreadySeen(i,6)) &
                           (~hasValue(i+1,1) | alreadySeen(i,5)))

reportC('after adjacency')

if args.verbose > 0:
    for i in range(4,n+1):
        D = C & ~mgr.interval(p[i-1],0)
        if i < n:
            D &= mgr.interval(p[i],0) 
        D.summary(name='paths of length ' + str(i))

print_solutions(C)
