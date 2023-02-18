"""Model checking of EG ~p on three-state structure.
"""

from __future__ import print_function

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(x,y)
    return TR.andAbstract(fromY, ycube)

from cudd import Cudd

mgr = Cudd()

n = 2

# Current and next state variables.
x = [mgr.bddVar(2*i,   'x' + str(i)) for i in range(n)]
y = [mgr.bddVar(2*i+1, 'y' + str(i)) for i in range(n)]

# Auxiliary cube for preimage computation.
ycube = y[1] & y[0]

# Print variable order.
print(' '.join((mgr.getVariableName(i) for i in range(2*n))))

# Transition relation.
T = ((~x[1] & ~x[0] & ~y[1] & y[0])
     | (~x[1] & x[0] & ~y[0])
     | (x[1] & ~x[0] & ~y[0]))

print('T', end=''); T.display(2*n)

# Initial state.
init = ~x[1] & ~x[0]

# Atomic propostions.
p = x[1] & ~x[0]
q = ~x[1] & x[0]

# EG ~p greatest fixpoint computation.
Z = ~p
zeta = mgr.bddZero()
while Z != zeta:
    zeta = Z
    print('Z',end=''); Z.summary(n); Z.printCover()
    Z &= pre(T, Z)

# Check inclusion of initial states.
print('EG ~p', ('holds' if init <= Z else 'does not hold'))
