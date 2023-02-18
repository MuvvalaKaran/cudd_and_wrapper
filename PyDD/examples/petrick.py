""" Enumerate all minimum-cost SOP covers of

    (A+B+C+D)(A'+B'+C'+D')

    using Petrick's method.  The prime implicants are pre-computed.
    For each of the six pairs (X,Y) of distinct variables, there are
    two prime implicants: X'Y and XY'.
"""
from __future__ import print_function
from functools import reduce
from cudd import Cudd

mgr = Cudd()

# One variable for each prime implicant.
names = ["A'B", "AB'", "A'C", "AC'", "A'D", "AD'",
         "B'C", "BC'", "B'D", "BD'", "C'D", "CD'"]

X = [mgr.bddVar(None, nm) for nm in names]
AnB, ABn, AnC, ACn, AnD, ADn, BnC, BCn, BnD, BDn, CnD, CDn = X

# Covering constraints for all minterms.
m = [mgr.bddOne()] * 16
m[1] = CnD | BnD | AnD
m[2] = BnC | CDn | AnC
m[3] = BnC | BnD | AnC | AnD
m[4] = AnB | BCn | BDn
m[5] = AnB | CnD | BCn | AnD
m[6] = AnB | CDn | AnC | BDn
m[7] = AnB | AnC | AnD
m[8] = ADn | ACn | ABn
m[9] = CnD | ACn | BnD | ABn
m[10] = BnC | ADn | CDn | ABn
m[11] = BnC | BnD | ABn
m[12] = ADn | ACn | BCn | BDn
m[13] = CnD | ACn | BCn
m[14] = ADn | CDn | BDn

# Characteristic functions of all prime covers.
P = reduce(lambda a, b: a & b, m)
# Restrict to covers of cardinality 4 (which is known to be minimal).
P &= mgr.cardinality(X, 4)

for cube in P.generate_cubes():
    print(' + '.join([str(X[i]) for i in range(len(X)) if cube[i] == 1]))
