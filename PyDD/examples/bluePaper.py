"""A Lewis Carrol's puzzle from Symbolic Logic."""

from __future__ import print_function, division, unicode_literals
from cudd import Cudd

def Implies(x,y):
    return ~x | y

m = Cudd()

# I can read the letter.
can = m.bddVar(None,'can')
# The letter is filed.
filed = m.bddVar(None,'filed')
# The letter is written on blue paper.
blue = m.bddVar(None,'blue')
# The letter is dated.
dated = m.bddVar(None,'dated')
# The letter is written on one sheet.
sheet = m.bddVar(None,'sheet')
# The letter is crossed.
crossed = m.bddVar(None,'crossed')
# The letter is written in black ink.
ink = m.bddVar(None,'ink')
# The letter is written in the third person.
third = m.bddVar(None,'third')
# The letter begins with "Dear Sir."
sir = m.bddVar(None,'sir')
# The letter is written by Brown.
brown = m.bddVar(None,'Brown')

variables = can & filed & blue & dated & sheet & crossed & ink & third & sir & brown
print(variables)

f = m.bddOne()

# All the dated letters in this room are written on blue paper.
f &= Implies(dated, blue)
# None of them are in black ink, except those that are written in the third person.
f &= Implies(~third, ~ink)
# I have not filed any of them that I can read.
f &= Implies(can, ~filed)
# None of them, that are written on one sheet, are undated.
f &= Implies(sheet, dated)
# All of them that are not crossed out are in black ink.
f &= Implies(~crossed, ink)
# All of them, written by Brown begin with "Dear Sir."
f &= Implies(brown, sir)
# All of them, written on blue paper, are filed.
f &= Implies(blue, filed)
# None of them, written on more than one sheet, are crossed.
f &= Implies(~sheet, ~crossed)
# None of those that begin with "Dear Sir," are written in the third person.
f &= Implies(sir, ~third)

print(f.twoLiteralClauses())
f.printTwoLiteralClauses()

f.display(name='f')

# We have the following chain of implications:
#
# brown -> sir -> Not(third) -> Not(ink) -> crossed ->
# sheet -> dated -> blue -> filed -> Not(can)
#
# Ww check that brown -> Not(can)
if f <= Implies(brown, ~can):
    print('implication')
else:
    print('no implication')
