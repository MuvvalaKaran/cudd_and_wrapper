"""Test of the ISOP functions."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()

n = 3
x = [m.bddVar(i, 'x' + str(i)) for i in range(n)]
m.zddVarsFromBddVars(2)
# We now name the variables.  Note that no new variables are created and
# that the ZDD variable names are distinct from the BDD/ADD variable names.
y = [m.zddVar(2*i,   'y' + str(i)) for i in range(n)]
z = [m.zddVar(2*i+1, 'z' + str(i)) for i in range(n)]

# Lower and upper bounds.
f = x[1]&~x[2]
g = x[1] | x[0]&~x[2]

# Here we only get a BDD between f and g with a simple cover.
h = f.isop(g)
h.display(n)
m.dumpDot([f, g, h],["f", "g", "h"])
if not f <= h <= g:
    raise RuntimeError("Incorrect result from 'isop.'")

# Here we also get the cover (as a ZDD).
(p,q) = f.isop(g,True)
if p != h:
    raise RuntimeError("Inconsistent results from two calls to 'isop.'")
q.printCover()
m.dumpDot([q], ["q"])

# Sanity check.
back = q.makeBddFromCover()
if back != h:
    raise RuntimeError("q should be a cover of h.")
