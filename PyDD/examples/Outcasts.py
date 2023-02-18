"""A knights and knaves puzzle by Smullyan.

   Who is the knight among the nine natives of the island?  
   Some may be outcasts: truthful on some days, liars on others.
"""

from __future__ import print_function

def native_name(i):
    """Return the name of the i-th native."""
    if i == 0:
        return "Archie"
    elif i == 1:
        return "Barab"
    elif i == 2:
        return "Cary"
    elif i == 3:
        return "Dreg"
    elif i == 4:
        return "Elmak"
    elif i == 5:
        return "Frisch"
    elif i == 6:
        return "Greg"
    elif i == 7:
        return "Hal"
    elif i == 8:
        return "Ilak"
    else:
        return "?"

from cudd import Cudd
mgr = Cudd()

# Declare and name variables.
n = 9
# tx: x is currently truthful
t = [mgr.bddVar(2*i, 't' + chr(ord('a') + i)) for i in range(n)]
ta,tb,tc,td,te,tf,tg,th,ti = t
# ox: x is an outcast
o = [mgr.bddVar(2*i+1, 'o' + chr(ord('a') + i)) for i in range(n)]
oa,ob,oc,od,oe,of,og,oh,oi = o

# A currently truthful, non-outcast native is a knight.
knights = [t[i] & ~o[i] for i in range(n)]

# Archie: The knight is either Cary, Elmak, Greg, or myself.
f = ta.iff(((ta & ~oa) | (tc & ~ oc) | (te & ~oe) | (tg & ~og)) &
           (~tb | ob) & (~td | od) & (~tf | of) & (~th | oh) & (~ti | oi))
# Barab: I'm an outcast.
f &= tb.iff(ob)
# Cary: Either Elmak is currently truthful or Greg is not.
f &= tc.iff(te | ~tg)
# Dreg: Archie lied.
f &= td.iff(~ta)
# Elmak: Barab and Dreg didn't both lie.
f &= te.iff(tb | td)
# Frisch: Cary lied.
f &= tf.iff(~tc)
# Greg: Archie is not the knight.
f &= tg.iff(~ta | oa)
# Hal: I am a knave and Ilak is an outcast.
f &= th.iff(~th & ~oh & oi)
# Ilak: I am a knave and Frisch lied.
f &= ti.iff(~ti & ~oi & ~tf)
# Exactly one of the nine natives is a knight.
g = mgr.cardinality(t, 1)
f &= g.vectorCompose(t, knights)

print("What simple facts are inferred from the natives' statements:",
      f.essential())

# Since knowing whether Hal is an outcast allowed the logician to
# solve the puzzle, the knight is unambiguously identified in one of
# the two cofactors of the constraints w.r.t. oh.
negative = f.cofactor(~oh)
positive = f.cofactor(oh)

# Inspect the constraints.
print("tototototototototo")
print("aabbccddeeffgghhii")
(negative & ~oh).printCover()

print("tototototototototo")
print("aabbccddeeffgghhii")
(positive & oh).printCover()

for i in range(n):
    if positive <= knights[i]:
        print(native_name(i) + " is the knight and Hal is an outcast.")
    if negative <= knights[i]:
        print(native_name(i) + " is the knight and Hal is not an outcast.")
