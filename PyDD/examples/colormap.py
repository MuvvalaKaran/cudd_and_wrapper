""" Compute colorings of a 5x5 Boolean such that the 16 2x2 submatrices
    are all distinct, the last row is identical to the first row and the
    last column is identical to the first column.
"""
from __future__ import print_function
from cudd import Cudd

def pattern(row1, row2, n):
    """ Return characterisitc function of n in terms of the four
        variables in row1 and row2 of a submatrix. """
    bits = row1 + row2
    lits = [bits[i] if (n & (1 << i)) else ~bits[i] for i in range(4)]
    return lits[0] & lits[1] & lits[2] & lits[3]
    
def convert(x):
    return "-" if x == 2 else str(x)

def list_to_string(prime):
    return " ".join(map(convert, prime))

mgr = Cudd()

# 5x5 matrix of variables.
x = [[mgr.bddVar() for j in range(5)] for i in range(5)]

f = mgr.bddOne()

# Each number from 0 to 15 must be the pattern of one of the 16 submatrices.
for n in range(16):
    g = mgr.bddZero()
    for i in range(4):
        for j in range(4):
            g |= pattern(x[i][j:j+2], x[i+1][j:j+2], n)
    f &= g

# The matrix has to be "toroidal."
for i in range(5):
    f &= x[0][i].iff(x[4][i])
    f &= x[i][0].iff(x[i][4])

f.summary()

for cube in f.generate_cubes():
    mat = [cube[i:i+5] for i in range(0, 25, 5)]
    print()
    for i in range(5):
        print(list_to_string(mat[i]))
