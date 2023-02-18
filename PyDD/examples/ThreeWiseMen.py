"""The three wise men with a hat problem puzzle.

   Three wise men wear hats that are either white or red.  There are at most
   two white hats.  Each man only sees the hats worn by the other two.
   Each man is asked in turn which color is the hat he wears.

   Asked which color is his hat, the first can't infer, the second neither,
   but the third can.  The conclusions of the wise men become public knowledge.
   That is, the second and third wise men know the first could
   not infer, and the third knows that the second couldn't either.

   The third wise man always reaches the conclusion that his hat is red when
   the first two men give up, regardless of the colors of their hats.

   The three men are assumed to be sound and complete reasoners as far as
   propositional logic goes.  This script is based on this assumption.
"""

from __future__ import print_function

def print_header():
    """Print variable names."""
    print("   wwwwwwwwwrrrrrrrrr", "www000111222000111222",
          "012012012012012012012", "_" * (n*(2*n+1)), sep="\n")

def learn(publ):
    """Turn facts about the world into knowledge."""
    facts = publ.existAbstract(kcube)
    print("facts", end="")
    facts.summary(n)
    facts.printCover()
    learned = mgr.bddOne()
    for i in range(n):
        posfact = facts.vectorCompose(w, kw[i])
        negfact = facts.vectorCompose(w, [~v for v in kr[i]])
        learned &= posfact & negfact
    return publ & learned

def report(i):
    """Report the conclusion of wise man i."""
    print("Wise man", i, end=" ")
    if public.isEssential(kw[i][i]):
        print("figures out his hat is white")
        return True
    elif public.isEssential(kr[i][i]):
        print("figures out his hat is red")
        return True
    else:
        print("cannot always figure out his hat's color")
        return False

def show(title, f):
    """Show public knowledge."""
    print(title, sep="", end="")
    f.summary()
    print_header()
    f.printCover()

from cudd import Cudd
mgr = Cudd()

n = 3 # number of wise men
# For each wise man we have 2*n+1 variables.  One tells his hat's color.
# The remaining 2*n represent his knowledge.
w = [mgr.bddVar(i, 'w' + str(i)) for i in range(n)] # the hat of i is white
kw = [[mgr.bddVar(n*(i+1)+j, 'k_' + str(i) + 'w_' + str(j)) for j in range(n)]
     for i in range(n)] # kw[i][j] is true iff i knows w[j] is true
kr = [[mgr.bddVar(n*(i+4)+j, 'k_' + str(i) + 'r_' + str(j)) for j in range(n)]
     for i in range(n)] # kr[i][j] is true iff i knows w[j] is false

# Cube of all knowledge variables used for existential quantification.
kcube = mgr.bddOne()
for kl in kw + kr:
    for kvar in kl:
        kcube &= kvar

checks = [~(w[0] & w[1] & w[2]), ~(w[1] & w[2]), ~w[2]]

# Seed public knowledge: there are at most two white hats.
public = mgr.cardinality(w, 0, 2)

# Basic rules of knowledge.
for i in range (n):
    for j in range(n):
        if i != j:
            # Each wise man sees the hats of the other men.
            public &= w[j].iff(kw[i][j]) & (~w[j]).iff(kr[i][j])
    # What is known must be true.
    public &= w[i].ite(~kr[i][i], ~kw[i][i])

for i in range(n):
    public = learn(public)
    show("Public knowledge before {0} makes his statement".format(i), public)
    print("Public knowledge",
          ("implies" if public <= checks[i] else "does not imply"), checks[i])
    if report(i):
        break
    # It becomes known that wise man i cannot infer his hat's color.
    public &= ~kw[i][i] & ~kr[i][i]
