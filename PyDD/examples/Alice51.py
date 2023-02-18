"""Alice in Puzzle-Land Tale 51, "The Most Interesting Case of All."

   This is a partially mechanized proof.
"""

from cudd import Cudd

class Solver:

    def __init__(self, mgr):
        self.manager = mgr
        self.constraints = mgr.bddOne()

    def add(self, constraint):
        self.constraints &= constraint

    def print(self, nvars=None, name=None):
        self.constraints.display(numVars=nvars,name=name)

    def constraints(self):
        return self.constraints

    def consequences(self, assumption):
        return (self.constraints & assumption).essential().constrain(assumption)

mgr = Cudd()

names = ['a1', 'a2', 'a3', 'ra', 'ta', 'fa', 'tb', 'fb', 'tc', 'fc']

a1,a2,a3,ra,ta,fa,tb,fb,tc,fc = [mgr.bddVar(name = nm) for nm in names]

s = Solver(mgr)

# One of A, B, C is a knight, one is a knave, and the third is a spy.
s.add(mgr.cardinality([ta,tb,tc],1))
s.add(mgr.cardinality([fa,fb,fc],1))
s.add(~(ta & fa) & ~(tb & fb) & ~(tc & fc))
sa,sb,sc = ~(ta|fa), ~(tb|fb), ~(tc|fc)

# If A says he's a spy, then A is not a knight.
s.add(a1.implies(~ta))
# If A says he's not a spy, then A is not a knave.
s.add((~a1).implies(~fa))

# If B is truthful, he answers yes if and only if A answered truthfully.
s.add(tb.implies(a2.iff(sa.iff(a1))))
# If B always lies, he answers no if and only if A answered truthfully.
s.add(fb.implies((~a2).iff(sa.iff(a1))))

s.print(nvars=8, name='After first two questions')

print('sa ->', s.consequences(sa))
print('sb ->', s.consequences(sb))
print('sc ->', s.consequences(sc))
print()

# By examination of the above results we conclude
# that a2 implies that C is not the spy.

s.add(a2)

s.print(nvars=8, name='F & a2')

# If A answers the third question.
s.add(ra.implies(ta.implies(a3.iff(sb))))
s.add(ra.implies(fa.implies((~a3).iff(sb))))
# If B answers the third question.
s.add((~ra).implies(tb.implies(a3.iff(sa))))
s.add((~ra).implies(fb.implies((~a3).iff(sa))))

s.print(name='with third question')

# Examination shows that if the judge could solve the problem,
# then it must be ra <-> a1 <-> a3.
s.add(ra.iff(a1.iff(a3)))

s.print(name='judge knows the answer')

# Impose the conditions of the two barrister friends.
allSame = (a1&a2&a3)|~(a1|a2|a3)
print('same answers ->', s.consequences(allSame))
twoNo = mgr.cardinality([a1,a2,a3],0,1)
print('2 no answers ->', s.consequences(twoNo))

# Examination shows that it's impossible for the friends to simultaneously have
# enough information to solve the puzzle.  Hence we assume that neither did.
s.add(~(allSame|twoNo))
s.print(name='final')

# Finally, we see that the spy must be B.
print('final ->', s.consequences(mgr.bddOne()))

