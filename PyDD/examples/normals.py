"""A knights, knaves, and normals puzzle. 

   You meet three inhabitants of the island of knights, knaves, and normals:
   A, B, and C.  You know that there is exactly one of each type among
   A, B, and C.

   Based on their statements, who is the knight, who is the knave,
   and who is the normal?
"""

from __future__ import print_function, division, unicode_literals

from cudd import Cudd
mgr = Cudd()

names = ['A', 'B', 'C']

ta,tb,tc = [mgr.bddVar(None,'t'+nm) for nm in names]
fa,fb,fc = [mgr.bddVar(None,'f'+nm) for nm in names]

common = (~(ta&fa) & ~(tb&fb) & ~(tc&fc) & mgr.cardinality([ta,tb,tc],1) &
          mgr.cardinality([fa,fb,fc],1))

"""
A says "C is the knave"
B says "A is the knight"
C says "C is the normal"
"""
F1 = ((~ta|fc) & (~fa|~fc) & (~tb|ta) & (~fb|~ta) & (~tc|(~tc&~fc)) &
      (~fc|tc|fc) & common)

print('F1 =', F1)

"""
A says "A is the knight"
B says "B is the knave"
C says "B is the knight"
"""

F2 = (~ta|ta) & (~fa|~ta) & (~tb|fb) & (~fb|~fb) & (~tc|tb) & (~fc|~tb) & common

print('F2 =', F2)

"""
A says "A is the knave"
B says "B is the knave"
C says "C is the knave"
"""

F3 = (~ta|fa) & (~fa|~fa) & (~tb|fb) & (~fb|~fb) & (~tc|fc) & (~fc|~fc) & common

print('F3 =', F3)

"""
A says "A is the knight"
B says "A is telling the truth"
C says "C is the normal"
"""

F4 = ((~ta|ta) & (~fa|~ta) & (~tb|ta) & (~fb|~ta) & (~tc|(~tc&~fc)) &
(~fc|tc|fc) & common)

print('F4 =', F4)

"""
A says "A is the knight"
B says "A is not the knave"
C says "B is not the knave"
"""

F5 = (~ta|ta) & (~fa|~ta) & (~tb|~fa) & (~fb|fa) & (~tc|~fb) & (~fc|fb) & common

print('F5 =', F5)

"""
A says "A is the knight"
B says "B is the knight"
C says "C is the knight"
"""

F6 = (~ta|ta) & (~fa|~ta) & (~tb|tb) & (~fb|~tb) & (~tc|tc) & (~fc|~tc) & common

print('F6 same as common =', F6.iff(common))

"""
A says "A is not the normal"
B says "B is not the normal"
C says "A is the normal"
"""

F7 = ((~ta|ta|fa) & (~fa|~(ta|fa)) & (~tb|tb|fb) & (~fb|~(tb|fb)) &
      (~tc|~(ta|fa)) & (~fc|ta|fa) & common)

print('F7 =', F7)

"""
A says "A is not the normal"
B says "B is not the normal"
C says "C is noy the normal"
"""

F8 = ((~ta|ta|fa) & (~fa|~(ta|fa)) & (~tb|tb|fb) & (~fb|~(tb|fb)) &
      (~tc|tc|fc) & (~fc|~(tc|fc)) & common)

print('F8 =', F8)
