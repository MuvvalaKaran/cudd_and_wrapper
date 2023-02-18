""" Build BDD from DIMACS file. 
"""
from __future__ import print_function
import argparse
import re
import matplotlib.pyplot as plt
import numpy as np

def readDIMACS(filename):
    """ Read a file in DIMACS format and return an array of clauses.
        Adapted from sympy.logic.utilities.dimacs.
        This version also parses files with multiple clauses on one line.
    """
    filestring = open(filename).read()
    lines = filestring.split('\n')
    pComment = re.compile('c.*')
    pPreamble = re.compile('p\s*cnf\s*(\d*)\s*(\d*)')

    clauses = []
    lst = []
    nums = []
    while len(lines) > 0:
        line = lines.pop(0)
        # Skip comments and preamble.
        if not pComment.match(line):
            if not pPreamble.match(line):
                nums.extend(line.rstrip('\n').split(' '))
                while len(nums) > 0:
                    lit = nums.pop(0)
                    if lit != '':
                        if int(lit) == 0:
                            if len(lst) > 0:
                                clauses.append(lst)
                                lst = []
                        else:
                            lst.append(int(lit))
    return clauses

def clauseBDD(clause):
    b = mgr.bddZero()
    for lit in clause:
        index = abs(lit)
        negative = lit < 0
        var = variables.get(index)
        if var is None:
            var = mgr.bddVar(None, str(index))
            variables[index] = var
        b |= ~var if negative else var
    return b

def linear(clauses, perm):
    f = mgr.bddOne()
    cnt = 0
    tot = len(clauses)
    for i in range(tot):
        c = clauseBDD(clauses[perm[i]])
        f &= c
        if args.verbose > 0:
            print('done with clause', cnt, 'out of', tot)
        cnt += 1
    return f

def gradual(clauses):

    if len(clauses) == 0:
        return mgr.bddOne()

    fncs = [clauseBDD(cl) for cl in clauses]
    nfncs = []
    while len(fncs) > 1:
        f1 = fncs.pop() & fncs.pop()
        nfncs.append(f1)
        if len(fncs) == 1:
            nfncs.append(fncs.pop())
        if len(fncs) == 0:
            fncs = nfncs
            nfncs = []
            if args.verbose > 0:
                print('completed one pass,', len(fncs), 'functions left')
    return fncs[0]

def plotCNF(clauses, rperm, cperm):
    xp = []
    xn = []
    yp = []
    yn = []
    for i in range(len(clauses)):
        c = rperm[i]
        for lit in clauses[c]:
            if lit > 0:
                plit = lit if cperm is None else cperm[lit-1] + 1
                xp.append(plit)
                yp.append(i)
            else:
                plit = -lit if cperm is None else cperm[-lit-1] + 1
                xn.append(plit)
                yn.append(i)
    plt.plot(xn, yn, '.r', xp, yp, '.b')
    plt.xlim([0.5,max(max(xp),max(xn))+0.5])
    plt.ylim([-0.5,len(rperm)-0.5])
    plt.show()

def depMat(clauses):
    # Create Boolean dependence matrix.  Literals and clauses start at 0.
    max_l = max(abs(lit) for row in clauses for lit in row)
    mat = np.zeros((len(clauses), max_l), dtype=bool)
    print(len(clauses), max_l, mat.dtype)
    for i in range(len(clauses)):
        for lit in clauses[i]:
            mat[i,abs(lit)-1] = True
    print('shape = ', mat.shape[0], mat.shape[1])
    # Count true elements in each row and column.
    clength = np.sum(mat,axis=0)
    rlength = np.sum(mat,axis=1)
    print('clength size', clength.size, 'rlength size', rlength.size)
    print('literals =', np.sum(mat,axis=(0,1)))
    print('min row length', min(rlength))
    # Initialize auxiliary structures.
    rperm = []
    cperm = []
    ractive = np.ones((mat.shape[0]), dtype=bool)
    cactive = np.ones((mat.shape[1]), dtype=bool)
    print('ractive', ractive.size, 'cactive', cactive.size)
    rpassive = 0
    cpassive = 0
    # Permute singleton rows to the top and their column to the left.
    for i in range(mat.shape[0]):
        if rlength[i] == 1:
            rperm.append(i)
            rpassive += 1
            ractive[i] = False
            colnum = np.nonzero(mat[i,:])[0][0]
            cperm.append(colnum)
            cpassive += 1
            cactive[colnum] = False
    if args.verbose > 0:
        print('After extraction of singleton rows:')
        print('rpassive', rpassive, 'cpassive', cpassive)
        if args.verbose > 1:
            print('rperm', rperm)
            print('cperm', cperm)
            print('ractive', ractive)
            print('cactive', cactive)
    # Deactivate empty columns.
    for j in range(mat.shape[1]):
        if not cactive[j]: continue
        found = False
        for i in range(mat.shape[0]):
            if ractive[i] and mat[i,j]:
                found = True
                break
        if not found:
            cactive[j] = False
            cpassive += 1
            cperm.append(j)
            print('deactivated column', j)
    # Deactivate rows that only contain inactive columns.
    for i in range(mat.shape[0]):
        if not ractive[i]: continue
        found = False
        for j in range(mat.shape[1]):
            if cactive[j] and mat[i,j]:
                found = True
                break
        if not found:
            ractive[i] = False
            rpassive += 1
            rperm.append(i)
            print('deactivated row', i)
    print('rpassive', rpassive, 'cpassive', cpassive)
    while rpassive < mat.shape[0] and cpassive < mat.shape[1]:
        # Find minimum row count.
        lmin = mat.shape[1] + 1
        minrows = set()
        for i in range(mat.shape[0]):
            if not ractive[i]: continue
            lrow = 0
            for j in range(mat.shape[1]):
                if cactive[j] and mat[i,j]:
                    lrow += 1
            if lrow <= lmin:
                if lrow < lmin:
                    lmin = lrow
                    minrows = set()
                minrows.add(i)
        if lmin == 0:
            print('lmin', lmin, 'type', type(lmin), 'minrows', minrows)
        # Find column with the most intersections with shortest rows.
        maxint = -1
        maxcol = -1
        for j in range(mat.shape[1]):
            if not cactive[j]: continue
            lcol = 0
            for i in range(mat.shape[0]):
                if i in minrows and mat[i,j]:
                    lcol += 1
            if lcol > maxint:
                maxint = lcol
                maxcol = j
        print('maxcol', maxcol)
        cperm.append(maxcol)
        cpassive += 1
        cactive[maxcol] = False
        if lmin == 1:
            for i in minrows:
                if mat[i,maxcol]:
                    rperm.append(i)
                    rpassive += 1
                    ractive[i] = False
    # Endgame.
    print('rpassive', rpassive, 'cpassive', cpassive)
    print('ractive', [i for i in range(mat.shape[0]) if ractive[i]])
    for i in range(mat.shape[0]):
        if ractive[i]:
            rperm.append(i)
    if args.verbose > 1:
        print('rperm', rperm)
        print('cperm', cperm)
        print('ractive', ractive)
        print('cactive', cactive)
        print(mat)
    icperm = [0] * len(cperm)
    for j in range(len(cperm)):
        icperm[cperm[j]] = j
    return (rperm, icperm)


if __name__ == "__main__":

    # Parse command line.
    parser = argparse.ArgumentParser(
        description='Build BDD from DIMACS file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', help='DIMACS file')
    parser.add_argument('-r', '--reorder',
                        help='dynamically reorder BDD variables',
                        action='store_true')
    parser.add_argument('-m', '--maximum',
                        help='maximum number of reorderings', type=int)
    parser.add_argument('-f', '--first',
                        help='threshold for first reordering', type=int)
    parser.add_argument('-v', '--verbose', help='increase verbosity',
                        action='count', default=0)
    parser.add_argument('-g', '--gradual', help='gradually build BDD',
                        action='store_true')
    parser.add_argument('-b', '--blt',
                        help='compute block lower-triangular form',
                        action='store_true')
    parser.add_argument('-p', '--plot', help='plot CNF', action='store_true')
    parser.add_argument('-s', '--stats', help='print BDD stats',
                        action='store_true')
    args = parser.parse_args()

    # Read DIMACS file.
    clauselist = readDIMACS(args.filename)
    #clauselist.sort(key=len)
    if args.verbose > 1:
        print('\n'.join([' '.join(['{:3}'.format(item) for item in row])
                         for row in clauselist]))

    if args.blt:
        (rperm,cperm) = depMat(clauselist)
    else:
        (rperm,cperm) = (range(len(clauselist)), None)
    if args.plot:
        plotCNF(clauselist, rperm, cperm)
    else:
        # Initialize BDD manager.
        from cudd import Cudd
        mgr = Cudd()
        if args.reorder:
            mgr.autodynEnable()
            if args.maximum:
                mgr.maxReorderings(args.maximum)
            if args.first:
                mgr.nextReordering(args.first)
            if args.verbose > 0:
                mgr.enableReorderingReporting()

        # Initialize function.
        variables = {}

        if args.gradual:
            f = gradual(clauselist)
        else:
            f = linear(clauselist, rperm)

        print('manager contains', len(variables), 'variables')
        print('f', end=''); f.summary(len(variables))
        if args.stats:
            mgr.printInfo()
