"""Classic Schneider's example that illustrates unique sensitization in ATPG.
   Here we use this example to show how to generate all tests for a
   stuck-at-1 fault by adding an OR gate to the fault site such that
   one input is 0 in the fault-free circuit and 1 in the faulty circuit.
   We then compute the Boolean difference of the resulting function w.r.t.
   the fault-activating input.
"""

from __future__ import print_function

def NAND(*args):
    """Compute NAND of all inputs."""
    res = mgr.bddOne()
    for x in args:
        res &= x
    return ~res

from cudd import Cudd
mgr = Cudd()
n = 4

a,b,c,d = (mgr.bddVar(i, chr(ord('a') + i)) for i in range(n))
activate = mgr.bddVar(4, 'activate')

e = NAND(a, c)
f = NAND(b, c)
g = NAND(b, d)
h = NAND(b, e)
i = NAND(a, f | activate)
j = NAND(d, f | activate)
k = NAND(c, g)
l = NAND(h, i, j, k)

print(l.booleanDiff(activate))
