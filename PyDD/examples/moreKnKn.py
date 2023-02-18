"""A knights and knaves puzzle. 

   You meet five inhabitants of the island of knights and knaves:
   Sally, Rex, Joe, Carl and Bart. 

   Sally claims that at least one of the following is true: that Bart
   is a knight or that Rex is a knight.

   Rex tells you that Bart is a knave. 

   Joe says that either Bart is a knave or Rex is a knave. 

   Carl claims that Rex is a knave. 

   Bart tells you that both Carl and Rex are knaves.

   Who is a knight and who is a knave?
"""

from __future__ import print_function, division, unicode_literals

from cudd import Cudd
mgr = Cudd()

names = ['Sally', 'Rex', 'Joe', 'Carl', 'Bart']

s,r,j,c,b = [mgr.bddVar(None,nm) for nm in names]

F = s.iff(b|r) & r.iff(~b) & j.iff(~b|~r) & c.iff(~r) & b.iff(~c&~r)

print(F)
