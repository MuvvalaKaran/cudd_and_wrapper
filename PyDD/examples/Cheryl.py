"""Epistemic model checking applied to the "Cheryl's birthday puzzle."

   Cheryl's birthday is in one of these dates:
     May        15, 16,         19
     June               17, 18
     July   14,     16
     August 14, 15,     17

   Cherly discloses the month to Albert and the day to Bernard.
   Albert and Bernard then have the following conversation:
     Albert: I don't know the date, but I know Bernard doesn't know it either.
     Bernard: At first I didn't know, but now I do.
     Albert: Then I also know when Cheryl's birthday is.
   When is Cheryl's birthday?
"""

from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse

month = ['May', 'June', 'July', 'August']
day = ['14', '15', '16', '17', '18', '19']

def print_solutions(solutions):
    """Convert common-knowledge BDD to list of solutions."""
    while not solutions.isZero():
        soln = solutions.pickOneMinterm(P) # ignore next-state variables
        solutions &= ~soln
        cube = soln.pickOneCube()          # convert to list of 0s and 1s
        X = int(''.join(map(str, cube[0:4:2])),2)
        Y = int(''.join(map(str, cube[4:10:2])),2)
        print(month[X], day[Y])

def reportC(title):
    """Print summary of common knowledge."""
    if args.verbose > 2:
        C.display(numVars=5, name=title)
    elif args.verbose > 0:
        C.summary(numVars=5, name=title)

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(P,Q)
    return TR.andAbstract(fromY, qcube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

def knowsWorld(TR):
    """Find plausible worlds that agent discerns from all other worlds."""
    return C & ~pre(TR & ~mgr.xeqy(P,Q), C)

# Parse command line.
parser = argparse.ArgumentParser(
    description='Solve the "Cherly\'s birthday" puzzle',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='count', default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

# Two bits for the month (May:0, June:1, July:2, August:3) and three bits
# for the day (14:0,...,19:5).
p = [[mgr.bddVar(2*i,   'm_' + str(i)) for i in range(2)],
     [mgr.bddVar(2*i+4, 'd_' + str(i)) for i in range(3)]]
q = [[mgr.bddVar(2*i+1, 'M_' + str(i)) for i in range(2)],
     [mgr.bddVar(2*i+5, 'D_' + str(i)) for i in range(3)]] # next-world variables

# These are used in predecessor computation.
# Flat lists of present and next state variables.
P = [x for r in p for x in r]
Q = [y for r in q for y in r]
# Cube for quantification.
qcube = reduce(lambda x, y: x & y, Q)

# Initial common knowledge: the date is one of the 10 that were announced.
C = ((mgr.interval(p[0],0) & mgr.interval(p[1],1,2)) |
     (mgr.interval(p[0],0) & mgr.interval(p[1],5)) |
     (mgr.interval(p[0],1) & mgr.interval(p[1],3,4)) |
     (mgr.interval(p[0],2) & mgr.interval(p[1],0)) |
     (mgr.interval(p[0],2) & mgr.interval(p[1],2)) |
     (mgr.interval(p[0],3) & mgr.interval(p[1],0,1)) |
     (mgr.interval(p[0],3) & mgr.interval(p[1],3)))

# World indistinguishability relations.  Albert cannot distinguish dates with
# the same month, while Bernard cannot distinguish dates with the same day.
Ta = mgr.xeqy(p[0],q[0])
Tb = mgr.xeqy(p[1],q[1])

if args.verbose > 1:
    Ta.summary(numVars=10, name='Albert\'s relation')
    Tb.summary(numVars=10, name='Bernard\'s relation')

# Find worlds in which Albert knows month and day.
# This is redundant because it is common knowledge that no month only has one day.
Ka1a = knowsWorld(Ta)
if args.verbose > 1:
    Ka1a.summary(numVars=5,name='Ka1a')

# Find the worlds where Albert knows that Bernard doesn't know the month.
Kb1 = knowsWorld(Tb)
Ka1b = knowsFact(Ta, ~Kb1)
if args.verbose > 1:
    Ka1b.summary(numVars=5,name='Ka1b')

# The fact that Albert knows that Bernard doesn't know becomes common knowledge.
C &= ~Ka1a & Ka1b
if args.verbose > 0:
    print('C after Albert says neither he nor Bernard knows')
    print_solutions(C)

# Find worlds where Bernard knows the date.
Kb2 = knowsWorld(Tb)

# The fact that now Bernad knows becomes common knowledge.
C &= Kb2
if args.verbose > 0:
    print('C after Bernard says he now knows')
    print_solutions(C)

# Find worlds where Albert now knows the date.
Ka2 = knowsWorld(Ta)

# The fact that Albert now knows becomes common knowledge. 
C &= Ka2
if args.verbose > 0:
    print('C after Albert says he knows too')
print_solutions(C)
