"""A knights and knaves puzzle quoted from Ray Smullyan's
   "What Is the Name of This Book?"

   According to this old problem, three of the inhabitants--A, B, and
   C--were standing together in a garden. A stranger passed by and
   asked A, "Are you a knight or a knave?" A answered, but rather
   indistinctly, so the stranger could not make out what he said. The
   stranger than asked B, "What did A say?" B replied, "A said that he
   is a knave." At this point the third man, C, said, "Don't believe
   B; he is lying!" The question is, what are B and C?

"""
from __future__ import print_function, division, unicode_literals

from cudd import Cudd
mgr = Cudd()

a,b,c = [mgr.bddVar(name=nm) for nm in ['A', 'B', 'C']]

print(b.implies(a.iff(~a)) & c.iff(~b))

