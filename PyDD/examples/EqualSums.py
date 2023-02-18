""" Alice chooses a number A between 1 and 10 and a number B between 11 and 20.
    Bob chooses a number X between 1 and 10 and a number Y between 11 and 20.
    It is known that
       \sum_{A \leq i \leq B} i = \sum_{X \leq i \leq Y} i = 90.
    In addition, it is known that A+B > X+Y.  What are A, B, X, Y?
"""

from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse

def print_solutions(solutions):
    """Convert BDD to list of solutions."""
    while not solutions.isZero():
        soln = solutions.pickOneMinterm()
        solutions &= ~soln
        cube = soln.pickOneCube()          # convert to list of 0s and 1s
        A = int(''.join(map(str, cube[0:m])),2)
        B = int(''.join(map(str, cube[m:2*m])),2)
        X = int(''.join(map(str, cube[2*m:3*m])),2)
        Y = int(''.join(map(str, cube[3*m:])),2)
        print('A:', A, 'B:', B+10, 'X:', X, 'Y:', Y+10)

def reportC(title):
    """Print summary of solutions."""
    if args.verbose > 1:
        C.display(numVars=n*m, name=title)
    elif args.verbose > 0:
        C.summary(numVars=n*m, name=title)

# Parse command line.
parser = argparse.ArgumentParser(
    description='Solve the "equal sums" puzzle',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='count', default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = 4 # number of numbers
m = 4 # number of bits in each number

# Instead of encoding B and Y with 5 bits, we encode B-10 and Y-10 with 4 bits.
p = [[mgr.bddVar(m*i+j, 'p_' + str(i) + '_' + str(j)) for j in range(m)]
     for i in range(n)]

C1 = mgr.interval(p[0],1,10) & mgr.interval(p[1],1,10)
# The sum of the integers from A to B equals 90.
cworlds = C1
while not cworlds.isZero():
    soln = cworlds.pickOneMinterm(p[0]+p[1])
    cworlds &= ~soln
    cube = soln.pickOneCube()
    p0 = int(''.join(map(str, cube[0:m])),2)
    p1 = int(''.join(map(str, cube[m:2*m])),2)
    if (p1+p0)*(p1-p0+1)+20*p1!=70:
        C1 &= ~soln

C2 = mgr.interval(p[2],1,10) & mgr.interval(p[3],1,10)
# The sum of the integers from X to Y equals 90.
cworlds = C2
while not cworlds.isZero():
    soln = cworlds.pickOneMinterm(p[2]+p[3])
    cworlds &= ~soln
    cube = soln.pickOneCube()
    p0 = int(''.join(map(str, cube[2*m:3*m])),2)
    p1 = int(''.join(map(str, cube[3*m:])),2)
    if (p1+p0)*(p1-p0+1)+20*p1!=70:
        C2 &= ~soln

C = C1 & C2

reportC('before final round')

# A+B > X+Y.
cworlds = C
while not cworlds.isZero():
    soln = cworlds.pickOneMinterm()
    cworlds &= ~soln
    cube = soln.pickOneCube()
    pint = [None] * n
    for i in range(n):
        pint[i] = int(''.join(map(str, cube[m*i:m*(i+1)])),2)
    if pint[0]+pint[1] <= pint[2]+pint[3]:
        C &= ~soln

reportC('after final round')
print_solutions(C)
