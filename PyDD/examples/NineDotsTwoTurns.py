"""Number of nonintersecting paths on a 3x3 grid that consist of
   exactly three segments.  Knight's moves are allowed.
   These paths have lengths between 4 and 7.
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

def sameRow(sol,i):
    return ((sol[i]-1) // 3) == ((sol[i+1]-1) // 3) == ((sol[i+2]-1) // 3)

def sameCol(sol,i):
    return (sol[i] % 3) == (sol[i+1] % 3) == (sol[i+2] % 3)

def sameDiag(sol,i):
    return ((sol[i:i+3] == [1, 5, 9]) or
            (sol[i:i+3] == [9, 5, 1]) or
            (sol[i:i+3] == [3, 5, 7]) or
            (sol[i:i+3] == [7, 5, 3]))

def threeSegments(sol):
    turns = 0
    for i in range(n-2):
        if sol[i+2] == 0:
            break
        if not (sameRow(sol,i) or sameCol(sol,i) or sameDiag(sol,i)):
            turns += 1
    #print(sol, turns)
    return turns == 2

def print_solutions(solutions):
    """Convert BDD to list of solutions."""
    while not solutions.isZero():
        soln = solutions.pickOneMinterm()
        solutions &= ~soln
        cube = soln.pickOneCube()          # convert to list of 0s and 1s
        pint = [None] * n
        for i in range(n):
            pint[i] = int(''.join(map(str, cube[m*i:m*(i+1)])),2)
        if threeSegments(pint):
            print(' '.join([str(x) for x in pint if x != 0]))

def hasValue(index, value, other=None):
    if other is None:
        other = value
    return mgr.interval(p[index], value, other)

# Parse command line.
parser = argparse.ArgumentParser(
    description='Count cell phone lock patterns',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='count', default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = 7 # number of numbers
m = 4 # number of bits in each number

p = [[mgr.bddVar(m*i+j, 'p_' + str(i) + '_' + str(j)) for j in range(m)]
     for i in range(n)]

C = mgr.bddOne()
for i in range(n):
    if i > 3:
        C &= mgr.interval(p[i],0,9)
    else:
        C &= mgr.interval(p[i],1,9)
    for j in range(i+1,n):
        C &= hasValue(i,0).ite(hasValue(j,0), ~mgr.xeqy(p[i],p[j]))

reportC('distinct between 0 and 9')

for i in range(n-1):
    C &= ~hasValue(i,1) | hasValue(i+1,2) | hasValue(i+1,4,6) | hasValue(i+1,8) | hasValue(i+1,0)
    C &= ~hasValue(i,2) | ~hasValue(i+1,8)
    C &= ~hasValue(i,3) | hasValue(i+1,2) | hasValue(i+1,4,6) | hasValue(i+1,8) | hasValue(i+1,0)
    C &= ~hasValue(i,4) | ~hasValue(i+1,6)
    C &= ~hasValue(i,6) | ~hasValue(i+1,4)
    C &= ~hasValue(i,7) | hasValue(i+1,8) | hasValue(i+1,4,6) | hasValue(i+1,2) | hasValue(i+1,0)
    C &= ~hasValue(i,8) | ~hasValue(i+1,2)
    C &= ~hasValue(i,9) | hasValue(i+1,8) | hasValue(i+1,4,6) | hasValue(i+1,2) | hasValue(i+1,0)

reportC('adjacency')

print_solutions(C)
