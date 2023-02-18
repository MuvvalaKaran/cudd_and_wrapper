""" Crossing a river with dogs: A cabbage-goat-wolf-like puzzle.

    Five humans and five dogs must cross a river in a boat that carries
    three passengers at most.  No dog can be left in the company of humans
    unless the dog's owner is also present.  One dog and all humans can 
    maneuver the boat.
"""

from __future__ import print_function, division, unicode_literals
from functools import reduce
from cudd import Cudd

conjoin = lambda a, b: a & b
disjoin = lambda a, b: a | b

"""---------------------------------------------------------------------
Functions that implement a BDD-based model checker for until formulae.
---------------------------------------------------------------------"""

class TransitionSystem(object):
    """ Simple transition system. """
    def __init__(self, variables, init, trans):
        self.variables = variables
        self.init = init
        self.trans = trans

def next_var(v):
    """ Returns primed variable. """
    return mgr.bddVar(v.index() + 1)

def image(TR, From, xcube, x, y):
    """ Computes image with transition relation. """
    ImgY = TR.andAbstract(From, xcube)
    return ImgY.swapVariables(y,x)

def preimage(TR, From, ycube, x, y):
    """ Computes preimage with transition relation. """
    FromY = From.swapVariables(x,y)
    return TR.andAbstract(FromY, ycube)

def forward_search(system, goal):
    """ Naively finds witness to "F goal" by forward reachability. """
    x = system.variables
    y = [next_var(v) for v in x]
    xcube = reduce(conjoin, x)
    Reached = New = system.init
    rings = [New]
    i = 0
    while New:
        print(i, ':', Reached.size(), 'nodes', Reached.count(len(x)), 'states')
        if not New <= ~goal:
            return (True, forward_witness(system, goal, rings))
        Img = image(system.trans, New, xcube, x, y)
        New = Img & ~Reached
        Reached |= New
        rings.append(New)
        i += 1
    return (False, None)

def forward_witness(system, goal, rings):
    """ Computes a witness to "F goal" property. """
    x = system.variables
    y = [next_var(v) for v in x]
    ycube = reduce(conjoin, y)
    witness = []
    tracestates = goal
    for ring in reversed(rings):
        interstates = tracestates.intersectionCube(ring)
        witness.append(interstates.cube())
        tracestates = preimage(system.trans, interstates, ycube, x, y)
    witness.reverse()
    return witness

"""---------------------------------------------------------------------
Functions used to build the model of the dogs' puzzle.
---------------------------------------------------------------------"""

def build_init(V):
    """ Returns the initial condition of the dogs' puzzle. """
    return reduce(conjoin, [~v for v in V])

def build_tr(V):
    """ Returns the transition relation of the dogs' puzzle. """
    V_ = [next_var(v) for v in V]
    H = V[0:N]
    H_ = V_[0:N]
    D = V[N:2*N]
    D_ = V_[N:2*N]
    boat = V[2*N]
    boat_ = V_[2*N]
    safe = build_invariant(V)
    safe.summary(name='safe', numVars=2*N+1)
    # The boat always shuttles back and forth between safe states.
    TR = safe & safe.swapVariables(V,V_) & (boat ^ boat_)
    # Only those on the same bank as the boat can board.
    TR &= reduce(conjoin,
                 [V[i].iff(boat) | V[i].iff(V_[i]) for i in range(2*N)])
    # The boat must carry at least one passenger capable of maneuvering it.
    TR &= reduce(disjoin,
                 [H[i] ^ H_[i] for i in range(N)] + [D[3] ^ D_[3]])
    # The boat must carry at most three passengers.
    TR &= mgr.cardinality([V[i] ^ V_[i] for i in range(2*N)], 0, 3)
    TR.summary(name='TR')
    return TR

def build_goal(V):
    """ Returns the target of the dogs' puzzle. """
    return reduce(conjoin, V)

def build_invariant(V):
    """ Returns the set of safe states of the dogs' puzzle. """
    H = V[0:N]
    D = V[N:2*N]
    safe = mgr.bddOne()
    for i in range(N):
        nohuman = reduce(conjoin, [D[i] ^ H[j] for j in range(N) if j != i])
        safe &= H[i].iff(D[i]) | nohuman
    return safe

"""---------------------------------------------------------------------
Main program.
---------------------------------------------------------------------"""

# Initialize BDD manager.
mgr = Cudd()

# Number of humans (and dogs).
N = 5

# Two state variables for each pair (human, dog).
# Current and next state variable pairs are interleaved.
# The last current-state variable is for the boat.
P = ([mgr.bddVar(4*i, 'h%d' % i) for i in range(N)] +
     [mgr.bddVar(4*i+2, 'd%d' % i) for i in range(N)] +
     [mgr.bddVar(4*N, 'b')])
P_ = ([mgr.bddVar(4*i+1, 'h%d_' % i) for i in range(N)] +
      [mgr.bddVar(4*i+3, 'd%d_' % i) for i in range(N)] +
      [mgr.bddVar(4*N+1, 'b_')])

dogs = TransitionSystem(
    variables = P,
    init = build_init(P),
    trans = build_tr(P))

goal = build_goal(P)

safe = build_invariant(P)

# Find witness to F goal
(res, witness) = forward_search(dogs, goal)

if res:
    print('Solution:')
    if witness:
        i = 0
        for c in witness:
            print('{0:2}'.format(i), ':', ' '.join(map(str,c[0:-2:2])))
            i += 1
else:
    print('No solution')
