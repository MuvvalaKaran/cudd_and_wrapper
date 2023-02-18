"""A knights and knaves puzzle.

   m*n islanders are arranged in an m x n grid.  Each makes two claims:

   1. If I'm excluded, there are more knights than knaves in my column.
   2. If I'm excluded, there are more knaves than knights in my row.

   How many knights are there out of the m*n islanders?

   The BDD sizes depend critially on the variable order.  The order that
   works well is by columns.  The order in which the claims are added to
   the overall BDD also matters.
"""

from __future__ import print_function, unicode_literals, division
import argparse
from cudd import Cudd

def rowclaim(i, j):
    """Builds row claim made by islander at position (i,j) of the grid."""
    row = [~T[i][k] for k in range(n) if k != j]
    return T[i][j].iff(mgr.cardinality(row, (n+1)//2, n-1))

def colclaim(i, j):
    """Builds column claim made by islander at position (i,j) of the grid."""
    col = [T[k][j] for k in range(m) if k != i]
    return T[i][j].iff(mgr.cardinality(col, (m+1)//2, m-1))

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve array of knights and knaves puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-r", "--rows", help="number of rows of the grid",
                    type=int, default=20)
parser.add_argument("-c", "--cols", help="number of columns of the grid",
                    type=int, default=25)
parser.add_argument("-s", "--solutions",
                    help="maximum number of solutions to be printed",
                    type=int, default=1)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)

args = parser.parse_args()
m = args.rows
n = args.cols

mgr = Cudd()

# t_i_j is true if and only if k_i_j is a knight
T = [[mgr.bddVar(j*m+i,   't_' + str(i) + '_' + str(j)) for j in range(n)]
     for i in range(m)]

if args.verbose > 1:
    # Print variable order.
    print('order:', ' '.join(mgr.bddOrder()))

claims = mgr.bddOne()

for j in range(n-1,-1,-1):
    cclaim = mgr.bddOne()
    for i in range(m):
        cclaim &= colclaim(i,j)
    claims &= cclaim

if args.verbose > 0:
    print('col claims:', claims.size(), 'nodes')

for i in range(m-1,-1,-1):
    rclaim = mgr.bddOne()
    for j in range(n):
        rclaim &= rowclaim(i, j)
    claims &= rclaim

if args.verbose > 0:
    if args.verbose > 2:
        claims.display(name='claims')
    else:
        print('claims:', claims.size(), 'nodes')

# Print sample solutions.
count = 0
for c in claims.generate_cubes():
    if count == args.solutions:
        break
    count += 1
    print('solution', count)
    for i in range(m):
        print(''.join([str(j) for j in c[i:(n-1)*m+i+1:m]]))

# Count knights in solutions.

# First count least knights.
least_knights = claims.shortestLength()

# Count least knaves by swapping each variable and its negation in claim BDD.
# Count most knights by subtracting least knaves from m*n.
vlist = mgr.bddVariables()
nvlist = [~v for v in vlist]
most_knights = m*n - claims.vectorCompose(vlist, nvlist).shortestLength()

if least_knights == most_knights:
    print('there are exactly', least_knights, 'knights in each of the',
          claims.count(), 'solutions')
else:
    print('there are between', least_knights, 'and', most_knights,
          'knights in the', claims.count(), 'solutions')
