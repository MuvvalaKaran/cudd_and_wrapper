"""A knights and knaves puzzle by Smullyan.

   Which of the men is a spy?  Mr. Dag, Mr. Egg, or Mr. Fen?
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3
# tmx: the man of couple x is truthful
tmd,tme,tmf = (mgr.bddVar(3*i,   'tm' + chr(ord('d') + i)) for i in range(n))
# twx: the woman of couple x is truthful
twd,twe,twf = (mgr.bddVar(3*i+1, 'tw' + chr(ord('d') + i)) for i in range(n))
# sx: the man of couple x is the spy
sd,se,sf = (mgr.bddVar(3*i+2, 's' + chr(ord('d') + i)) for i in range(n))

# Mr. Dag : I am not the spy.
f = tmd.iff(~sd)
# Mrs. Dag: Mr. Egg is the spy.
f &= twd.iff(se)
# Mr. Egg : Mr. Dag is truthful.
f &= tme.iff(tmd)
# Mrs. Egg: Mr. Fen is the spy.
f &= twe.iff(sf)
# Mr. Fen : I am not the spy.
f &= tmf.iff(~sf)
# Mrs. Fen: Mr. Dag is the spy.
f &= twf.iff(sd)
# Exactly one of Mr. Dag, Mr. Egg, and Mr. Fen is the spy.
f &= mgr.cardinality([sd,se,sf], 1)
# In one couple both spouses are truthful.
f &= (tmd & twd) | (tme & twe) | (tmf | twf)
# In one couple both spouses are liars.
f &= ~(tmd | twd) | ~(tme | twe) | ~(tmf | twf)
# In one couple exaclty one of the spouses is truthful.
f &= (tmd ^ twd) | (tme ^ twe) | (tmf ^ twf)

if f <= sd:
    print("Mr. Dag is the spy.")
elif f <= se:
    print("Mr. Eff is the spy.")
elif f <= sf:
    print("Mr. Fen is the spy.")
else:
    print("Ambiguous constraints.")

print("mwrmwrmwr")
print("dddeeefff")
f.printCover()
