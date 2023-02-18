"""
Find consistent answer(s) to multiple choice question.
"""
from __future__ import print_function
from cudd import Cudd

mgr = Cudd()

a1,a2,a3,a4,a5,a6 = (mgr.bddVar(i, 'a' + str(i+1)) for i in range(6))

F = (
    a1.iff(a2 & a3 & a4 & a5 & a6)      # all of the following
    & a2.iff(~(a3 | a4 | a5 | a6))      # none of the following
    & a3.iff(a1 & a2)                   # all of the above
    & a4.iff(a1 | a2 | a3)              # one of the above
    & a5.iff(~(a1 | a2 | a3 | a4))      # none of the above
    & a6.iff(~(a1 | a2 | a3 | a4 | a5)) # none of the above
)

print(F)
