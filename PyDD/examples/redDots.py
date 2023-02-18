""" Find the largest number of red dots one can place on a rectangular
    grid so that no four dots are the corners of a rectangle whose sides
    are parallel to the grid lines.

    The values for R(n,n) form sequence A072567.
"""
from __future__ import print_function
from cudd import Cudd
import argparse

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve red dots problem",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-r", "--rows", help="number of rows of the grid",
                    type=int, default=3)
parser.add_argument("-c", "--cols", help="number of columns of the grid",
                    type=int, default=4)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
parser.add_argument("--reorder", help="dynamically reorder BDD variables",
                    action="store_true")
parser.add_argument("-s", "--symmetry", help="apply symmetry reduction",
                    action="store_true")
args = parser.parse_args()

N = args.rows
M = args.cols

mgr = Cudd()

if args.reorder:
    mgr.autodynEnable()
    mgr.enableReorderingReporting()

x = [[mgr.bddVar() for j in range(M)] for i in range(N)]

f = mgr.bddOne()

if args.symmetry:
    # Enforce lexicographic ordering of grid rows.
    for i in range(N-1):
        f &= mgr.inequality(0, x[i], x[i+1])
    # Enforce lexicographic ordering of grid columns.
    bycol = [[x[i][j] for i in range(N)] for j in range(M)]
    for i in range(M-1):
        f &= mgr.inequality(0, bycol[i], bycol[i+1])
    if args.verbose > 0:
        print('antisymm', end=''); f.summary()

# Add forbidden rectangle constraints.
for i in range(N-1):
    for j in range(M-1):
        g = mgr.bddOne()
        for k in range(i+1,N):
            for l in range(j+1,M):
                g &= x[k][j] | x[i][l] | x[k][l]
        f &= x[i][j] | g

print('f', end=''); f.summary()
(path, length) = f.shortestPath()
print('path = ', end='')
path.printCover()
print('max dots =', N*M-length)
g = f & mgr.cardinality([x[i][j] for i in range(N) for j in range(M)],length)
print('optimal', end=''); g.summary()
