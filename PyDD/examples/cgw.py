"""Model of the cabbage-goat-wolf puzzle.
"""

from __future__ import print_function

def left(v):
    """True if v is on the left bank."""
    return ~v

def right(v):
    """True if v is on the right bank."""
    return v

def same(v1,v2):
    """True if v1 and v2 are on the same bank."""
    return v1.iff(v2)

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(x,y)
    return TR.andAbstract(fromY, ycube)

from cudd import Cudd

mgr = Cudd()

Left = mgr.bddZero()
Right = mgr.bddOne()

names = ["b", "c", "g", "w", "s1", "s0"]
namesp = ["b'", "c'", "g'", "w'"]
n = 4

b,c,g,w = (mgr.bddVar(2*i, names[i]) for i in range(n))
bp,cp,gp,wp = (mgr.bddVar(2*i+1, namesp[i]) for i in range(n))
s1,s0 = (mgr.bddVar(2*n+i, names[n+i]) for i in range(2))

print(' '.join((mgr.getVariableName(i) for i in range(2*n-2))))

# The combination s1 & s0 selects none.
selc = ~s1 & ~s0
selg = ~s1 & s0
selw = s1 & ~s0

# Transition relations of individual agents.  The boat changes side
# at each transition.
tb = bp.iff(~b)
tc = cp.iff((selc & same(b,c)).ite(~c,c))
tg = gp.iff((selg & same(b,g)).ite(~g,g))
tw = wp.iff((selw & same(b,w)).ite(~w,w))

T = (tb & tc & tg & tw).existAbstract(s1 & s0)
print('T', end='')
T.display(2*n)

# Everybody is initially on the left bank.
init = left(b) & left(c) & left(g) & left(w)

# Atomic propostions.
safe = same(b,g) | (same(c,b) & same(b,w))
final = right(b) & right(c) & right(g) & right(w)

# Auxiliary variables for preimage computation.
x = [b,c,g,w]
y = [bp,cp,gp,wp]
ycube = bp & cp & gp & wp

# safe Until final computation.
Z = New = final
while New:
    print('Z',end='')
    Z.summary(n)
    Z.printCover()
    Pre = pre(T, New)
    New = Pre & safe & ~Z
    Z |= New

print('The puzzle', ('has' if init <= Z else 'does not have'), 'a solution')
