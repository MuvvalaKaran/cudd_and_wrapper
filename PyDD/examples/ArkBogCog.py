"""A knights and knaves puzzle by Smullyan.

   Who is the royal couple among the Arks, the Bogs, and the Cogs?
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3
# tmx: the man of couple x is truthful
tma,tmb,tmc = (mgr.bddVar(3*i,   'tm' + chr(ord('a') + i)) for i in range(n))
# twx: the woman of couple x is truthful
twa,twb,twc = (mgr.bddVar(3*i+1, 'tw' + chr(ord('a') + i)) for i in range(n))
# rx: x is the royal couple
ra,rb,rc = (mgr.bddVar(3*i+2, 'r' + chr(ord('a') + i)) for i in range(n))
# kbi: the king was born in Italy
kbi = mgr.bddVar(3*n, 'kbi')
# kbs: the king was born in Spain
kbs = mgr.bddVar(3*n+1, 'kbs')

# Mr. Ark : I am not the king.
f = tma ^ ra
# Mrs. Ark: The king was born in Italy.
f &= twa.iff(kbi)
# Mr. Bog : Mr. Ark is not the king.
f &= tmb ^ ra
# Mrs. Bog: The king was really born in Spain.
f &= twb.iff(kbs)
# Mr. Cog : I am not the king.
f &= tmc ^ rc
# Mrs. Cog: Mr. Bog is the king.
f &= twc.iff(rb)
# Exactly one of the Arks, the Bogs, and the Cogs is the royal couple.
f &= mgr.cardinality([ra,rb,rc], 1)
# The king cannot be born in both Italy and Spain.
f &= ~(kbi & kbs)
# No couple consists of two liars.
f &= (tma | twa) & (tmb | twb) & (tmc | twc)

if f.isEssential(ra):
    print("The Arks are the royal couple.")
elif f.isEssential(rb):
    print("The Bogs are the royal couple.")
elif f.isEssential(rc):
    print("The Cogs are the royal couple.")
else:
    print("Ambiguous constraints.")

# The birthplace of the king is not known, though without the statements of
# Mrs. Ark and Mrs. Bog there is no unique answer for who's the royal couple.
# The key point is that Mrs. Ark and Mrs. Bog disagree; hence one of them is
# a liar, which means that at least one of their husbands is truthful.
print("mwrmwrmwrbb")
print("aaabbbcccis")
f.printCover()

f.essential().printCover()
