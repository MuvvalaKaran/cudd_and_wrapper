"""Compute all solutions of a Sudoku puzzle.

This script relies on BDDs to do the heavy lifting.
"""

from __future__ import print_function
import sys
import re
import tempfile
import time
import argparse

def check_number(value):
    """Check that the number of solutions is a nonnegative integer."""
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            "%s is not a nonnegative integer" % value)
    return ivalue

def print_essential(c):
    ess = c.essential()
    print('ess'); ess.printCover()
    converter = lambda x : "-" if x == 2 else str(x)

    # Build solution matrix.  Shift 0-8 to 1-9 by starting from 1.
    for model in ess.generate_primes():
        modstr = "".join((converter(x) for x in model))
        matrix = [""] * n
        for i in range(n):
            matrix[i] += modstr[4*i:4*(i+1)]

        separ = "+------" * 9 + "+"
        print(separ)
        for i in range(9):
            row = "|"
            for j in range(9):
                row += " " + matrix[9 * i + j] + " |"
            print(row, '\n', separ, sep='')

from cudd import Cudd

def bounds(mgr, x, index):
    """
    Generate bound constraints for a cell.
    """
    var = 4 * index
    return mgr.interval(x[var:var+4], 0, 8)

def unit(mgr, x, index, value):
    """
    Generate constraints for a given.
    """
    var = 4 * index
    return mgr.interval(x[var:var+4], value, value)

def diseq(mgr, x, fc, sc, matrix, gp):
    """
    Generate disequality constraints for two cells.
    """
    f0 = 4 * fc
    s0 = 4 * sc
    if gp.match(matrix[fc]):
        if matrix[fc] == matrix[sc]:
            raise ValueError("Inconsistent givens")
        elif gp.match(matrix[sc]):
            return mgr.bddOne()
        else:
            value = int(matrix[fc]) - 1
            return ~mgr.interval(x[s0:s0+4], value, value)
    elif gp.match(matrix[sc]):
        value = int(matrix[sc]) - 1
        return ~mgr.interval(x[f0:f0+4], value, value)
    else:
        return ~mgr.xeqy(x[f0:f0+4], x[s0:s0+4])

# Main program.

# Parse command line.
parser = argparse.ArgumentParser(
    description="Find all solutions of a Sudoku puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--number",
                    help="maximum number of solutions to be printed",
                    type=check_number, default=None)
parser.add_argument("-e", "--essential",
                    help="print essential entries (including givens",
                    action="store_true")
parser.add_argument("-a", "--additional",
                    help="conjoin hypersudoku constraints",
                    action="store_true")
parser.add_argument("-k", "--antiknight",
                    help="conjoin antiknight constraints",
                    action="store_true")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
args = parser.parse_args()

startTime = time.time()
n = 81 # number of cells

# Read the input matrix.
matrix = []
for line in sys.stdin:
    if line.startswith("|"):
        row = line.rstrip().split("|")[1:-1]
        matrix.extend(row)

if len(matrix) != n:
    raise ValueError("wrong number of items in matrix")

mgr = Cudd()
x = [mgr.bddVar(i, 'x' + str(i)) for i in range(4*n)]
c = mgr.bddOne() # Overall constraints
g = mgr.bddOne() # Constraints due to givens

givep = re.compile('\s*[1-9]\s*')
givens = sum(givep.match(m) != None for m in matrix)
if args.verbose > 0:
    print(givens , 'givens')

# Build constraint BDD.  The order in which constraints are
# added is linked to the variable order.

# Add bound and given constraints.
for i in range(len(matrix)):
    if givep.match(matrix[i]):
        g &= unit(mgr, x, i, int(matrix[i]) - 1)
    else:
        c &= bounds(mgr, x, i)

if args.verbose > 0:
    print('bnd', end=''); c.summary(n*4)

# Add uniqueness constraints for rows.
for i in range(9):
    for j in range(8):
        for k in range(j+1, 9):
            fc = 9 * i + j
            sc = 9 * i + k
            c &= diseq(mgr, x, fc, sc, matrix, givep)

if args.verbose > 0:
    print('row', end=''); c.summary(n*4)
e = c.essential()
c = c.constrain(e)
#sys.stdout.write('ess'); e.summary(n*4)

# Add uniqueness constraints for regions.
for i in range(9):
    for j in range(8):
        for k in range(j+1, 9):
            fc = 3 * (i % 3) + 27 * (i // 3) + (j % 3) + 9 * (j // 3)
            sc = 3 * (i % 3) + 27 * (i // 3) + (k % 3) + 9 * (k // 3)
            if (fc // 9) != (sc // 9): # avoid duplicates, but not all of them
                c &= diseq(mgr, x, fc, sc, matrix, givep).constrain(e)

if args.verbose > 0:
    print('reg', end=''); c.summary(n*4)

if args.additional:
    """ Add "Hypersudoku" constraints. """
    srow = [10, 14, 46, 50]
    for i in range(4):
        for j in range(8):
            for k in range(j+1, 9):
                fc = srow[i] + (j % 3) + 9 * (j // 3)
                sc = srow[i] + (k % 3) + 9 * (k // 3)
                if (fc // 9) != (sc // 9) and (fc % 9) != (sc % 9):
                    c &= diseq(mgr, x, fc, sc, matrix, givep).constrain(e)

if args.antiknight:
    """ Add "anti-knight" constraints. """
    for i in range(8):
        for j in range(9):
            kc = mgr.bddOne()
            if i + 2 < 9 and j + 1 < 9:
                fc = j + 9 * i
                sc = (j+1) + 9 * (i+2)
                kc &= diseq(mgr, x, fc, sc, matrix, givep)
            if i + 1 < 9 and j + 2 < 9:
                fc = j + 9 * i
                sc = (j+2) + 9 * (i+1)
                kc &= diseq(mgr, x, fc, sc, matrix, givep)
            if i + 2 < 9 and j > 0:
                fc = j + 9 * i
                sc = (j-1) + 9 * (i+2)
                kc &= diseq(mgr, x, fc, sc, matrix, givep)
            if i + 1 < 9 and j > 1:
                fc = j + 9 * i
                sc = (j-2) + 9 * (i+1)
                kc &= diseq(mgr, x, fc, sc, matrix, givep)
            c &= kc.constrain(e)
        if args.verbose > 1:
            print('tmp', end=''); c.summary(n*4)

if args.verbose > 0:
    print('ext', end=''); c.summary(n*4)
e2 = c.essential()
c = c.constrain(e2)
e &= e2
#sys.stdout.write('ess'); e.summary(n*4)

# Add uniqueness constraints for columns.
for j in range(9):
    cc = mgr.bddOne()
    for i in range(8):
        for k in range(i+1, 9):
            if (i // 3) != (k // 3): # avoid duplicates
                fc = j + 9 * i
                sc = j + 9 * k
                cc &= diseq(mgr, x, fc, sc, matrix, givep)
    c &= cc.constrain(e)
    if args.verbose > 1:
        print('tmp', end=''); c.summary(n*4)

if args.verbose > 0:
    print('col', end=''); c.summary(n*4)

c &= g & e
if args.verbose > 0:
    print('sol', end=''); c.summary(n*4)


if args.essential:
    print_essential(c)

# Print one matrix for each model of the constraint BDD.
# We rely on the fact that the primes of c are minterms.
count = 0
for model in c.generate_primes():
    if args.number != None and args.number == count:
        break
    count += 1
    if len(model) != n*4:
        raise ValueError("Wrong number of variables in model")

    # Build solution matrix.  Shift 0-8 to 1-9 by starting from 1.
    matrix = [1] * n
    for i in range(n):
        fourb = int("".join((str(x) for x in model[4*i:4*(i+1)])), 2)
        matrix[i] += fourb

    separ = "+---" * 9 + "+"
    print(separ)
    for i in range(9):
        row = "|"
        for j in range(9):
            row += " " + str(matrix[9 * i + j]) + " |"
        print(row, '\n', separ, sep='')

nsol = c.count()
if nsol > 1:
    print(nsol, 'solutions')
print('CPU time = {0} s'.format(time.time() - startTime))
