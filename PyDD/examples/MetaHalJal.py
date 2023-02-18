"""A knights and knaves puzzle by Smullyan.

   Three logicians separately question Hal, but none of them can determine
   the types of Hal and Jal.
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3 # number of questions
y = [mgr.bddVar(i, 'y' + str(i)) for i in range(n)]
th = mgr.bddVar(3, 'th')     # Hal is truthful
tj = mgr.bddVar(4, 'tj')     # Jal is truthful

# The questions asked of Hal:
# 1. Are you both knights?
# 2. Are you both knaves?
# 3. Are you a knight and is Jal a knave?
question = [th & tj, ~th & ~ tj, th & ~tj]
f = [y[i].iff(th.iff(question[i])) for i in range(n)]

answers = []
knowledge = mgr.bddOne()
for i in range(n):
    pos_essent = f[i].cofactor(y[i]).essential()
    neg_essent = f[i].cofactor(~y[i]).essential()
    if pos_essent.isOne() and not neg_essent.isOne():
        answers.append(y[i])
        knowledge &= f[i].cofactor(y[i])
    elif neg_essent.isOne() and not pos_essent.isOne():
        answers.append(~y[i])
        knowledge &= f[i].cofactor(~y[i])

print("Answers:", ", ".join((str(a) for a in answers)))
print("What we know:", knowledge)
