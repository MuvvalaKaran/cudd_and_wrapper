"""Alice in Puzzle-Land, tale 87, "The Most Baffling Case of All."
   Solution using epistemic logic.
"""

from cudd import Cudd
from functools import reduce

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(cs,ns)
    return TR.andAbstract(fromY, ncube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

conjoin = lambda x, y: x & y
mgr = Cudd()

defendants = ['A', 'B', 'C']
n = len(defendants)

# For each defendant we need 3 current-world variables, indicating whether
# the defendant
# - is truthful
# - makes an accusatory or exculpatory statement
# - is guilty or innocent
# We also need three matching next-world variables.
#
# Finally, we need a variable pair to encode Tweedledum's choice of question.

# Truthfuleness of defendants.
tc = [mgr.bddVar(6*i,   'tc' + defendants[i]) for i in range(n)]
tn = [mgr.bddVar(6*i+1, 'tn' + defendants[i]) for i in range(n)]
# Accusatory statements.
ac = [mgr.bddVar(6*i+2, 'ac' + defendants[i]) for i in range(n)]
an = [mgr.bddVar(6*i+3, 'an' + defendants[i]) for i in range(n)]
# Guilty.
gc = [mgr.bddVar(6*i+4, 'gc' + defendants[i]) for i in range(n)]
gn = [mgr.bddVar(6*i+5, 'gn' + defendants[i]) for i in range(n)]
# Tweedledum question (second vs. third defendant's question).
uc = mgr.bddVar(18, 'uc')
un = mgr.bddVar(19, 'un')

cs = tc + ac + gc + [uc]
ns = tn + an + gn + [un]

ncube = reduce(conjoin, ns)

# Common knowledge.
# If a defendant is accused by a truthful defendant, he's guilty.
C = (tc[0].iff(ac[0].iff(gc[0])) &
     tc[1].iff(ac[1].iff(gc[1])) &
     tc[2].iff(ac[2].iff(gc[0])))
# At most one of the statements is true.
C &= mgr.cardinality(tc,0,1)
# Exactly one of the defendants is guilty.
C &= mgr.cardinality(gc,1)

print('The', C.count(9), 'worlds that are common knowledge')
C.cubes('')

# The Jabberwocky knows the answers of all defendants.
Rjw = reduce(conjoin, [ac[i].iff(an[i]) for i in range(n)])
Rjw.display(numVars=6, name='WIR Jabberwocky')

JwKnows = mgr.bddZero()
for i in range(n):
    JwKnows |= knowsFact(Rjw, gc[i])

print('The', JwKnows.count(9), 'worlds where the Jabberwocky knows the culprit')
JwKnows.cubes('')

# Every subsequent character knows that the Jabberwocky solved the puzzle.
C = JwKnows

# Tweedledee knows the answer of the first defendant.
Rte = ac[0].iff(an[0])
Rte.display(numVars=2, name='WIR Tweedledee')

TdeeKnows = mgr.bddZero()
for i in range(n):
    TdeeKnows |= knowsFact(Rte, gc[i])

print('The', TdeeKnows.count(9), 'world where Tweedledee knows the culprit')
TdeeKnows.cubes('')

# Tweedledum knows either the answer of the second defendant or
# the answer of the thord defendant.
Rtu = uc.ite(ac[1].iff(an[1]), ac[2].iff(an[2])) & uc.iff(un)
Rtu.summary(numVars=6, name='WIR Tweedledum')
Rtu.printCover()

TdumKnows = mgr.bddZero()
for i in range(n):
    TdumKnows |= knowsFact(Rtu, gc[i])

print('The', TdumKnows.count(10), 'worlds where Tweedledum knows the culprit')
TdumKnows.cubes('')

# Humpty-Dumpty knows which defender's answer Tweedledum knows.
Rhd = uc.iff(un)
Rhd.display(numVars=2, name='WIR Humpty Dumpty')

# Humpty Dumpty knows neither Tweedledee nor Tweedledum solved the puzzle. 
C &= ~TdeeKnows & ~TdumKnows
HdKnows = mgr.bddZero()
for i in range(n):
    HdKnows |= knowsFact(Rhd, gc[i])

print('The', HdKnows.count(10), 'worlds where Humpty Dumpty knows the culprit')
HdKnows.cubes('')

# Alice knows that Humpty Dumpty solved the problem.
C = HdKnows
print('known facts')
C.essential().cubes('')
print('guilty')
C.existAbstract(reduce(conjoin,tc+ac+[uc])).cubes()
