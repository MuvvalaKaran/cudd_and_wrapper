"""Solver for the Instant Insanity Puzzle.

   Four cubes are given, whose faces are colored with one of four colors.
   We want to find a way to stack the cubes so that on each of the four
   large faces of the resulting tower all color appear once.
"""

from __future__ import print_function, division, unicode_literals
from cudd import Cudd

def get_cycles(lst):
    """Get directed cycles from undirected graph."""
    oedge = set() # of colors with outgoing arcs
    iedge = set() # of colors with incoming arcs
    edges = set([tuple(e) for e in lst])
    # Start cycles with first edge in lst.
    e = tuple(lst[0])
    edges.remove(e)
    cycles = [(e[0],e[2],e[1])]
    oedge.add(e[0])
    iedge.add(e[1])
    
    while edges:
        lastn = cycles[-1][2] # last node on path
        reverse = False
        if lastn in oedge:
            # Start new cycle
            e = edges.pop()
        else:
            for e in edges:
                if lastn == e[0]:
                    break
                elif lastn == e[1]:
                    reverse = True
                    break
            edges.remove(e)
        if reverse:
            cycles.append((e[1],e[2],e[0]))
            oedge.add(e[1])
            iedge.add(e[0])
        else:
            cycles.append((e[0],e[2],e[1]))
            oedge.add(e[0])
            iedge.add(e[1])
    return cycles
    

def print_solution(mgr, C):
    """Pretty print solutions."""

    """From each cube of the constraint BDD extract the positive literals,
    which correspond to the chosen edges, and collect then in two lists,
    one for the left-right edges, and one for the front-back edges.  These
    edges define two undirected graphs, which consists of one or more
    cycles each.  Call get_cycles to extract the cycles and orient them,
    and fill matrix of left-front-right-back faces with results.
    """
    for soln in C.generate_cubes():
        lrlist = []
        fblist = []
        for i in range(mgr.size()):
            if soln[i] == 1:
                varname = mgr.getVariableName(i)
                if varname.startswith('lr'):
                    lrlist.append(varname[2:])
                else:
                    fblist.append(varname[2:])
        lrcycles = get_cycles(lrlist)
        #print('LR:', ','.join([''.join(e) for e in lrcycles]))
        fbcycles = get_cycles(fblist)
        #print('FB:', ','.join([''.join(e) for e in fbcycles]))

        mat = [[' ' for j in range(n)] for i in range(n)]
        for e in lrcycles:
            cube = int(e[1]) - 1
            mat[cube][0] = e[0]
            mat[cube][2] = e[2]
        for e in fbcycles:
            cube = int(e[1]) - 1
            mat[cube][1] = e[0]
            mat[cube][3] = e[2]
        print('-' * 9)
        print('\n'.join([' '.join([mat[i][j] for j in range(n)]) for i in range(n)]))
            
        

n = 4

"""First we solve the puzzle for these four cubes.

       +---+                +---+
       | R |                | R |
   +---+---+---+---+    +---+---+---+---+
   | R | Y | G | B |    | R | Y | B | G |
   +---+---+---+---+    +---+---+---+---+
       | R |                | Y |
       +---+                +---+

       +---+                +---+
       | G |                | B |
   +---+---+---+---+    +---+---+---+---+
   | B | B | R | Y |    | G | Y | R | G |
   +---+---+---+---+    +---+---+---+---+
       | G |                | Y |
       +---+                +---+
"""

mgr = Cudd()

# One variable for each pair of opposing faces of each cube and each
# pair of large faces of the stack.  In the names "lr" stand for
# "left-right" and "fb" stands for "front-back".

lrrr1, lrrg1, lrby1 = (mgr.bddVar(None, nm)
                       for nm in ['lrrr1', 'lrrg1', 'lrby1'])
fbrr1, fbrg1, fbby1 = (mgr.bddVar(None, nm)
                       for nm in ['fbrr1', 'fbrg1', 'fbby1'])

lrrb2, lrry2, lrgy2 = (mgr.bddVar(None, nm)
                       for nm in ['lrrb2', 'lrry2', 'lrgy2'])
fbrb2, fbry2, fbgy2 = (mgr.bddVar(None, nm)
                       for nm in ['fbrb2', 'fbry2', 'fbgy2'])

lrrb3, lrby3, lrgg3 = (mgr.bddVar(None, nm)
                       for nm in ['lrrb3', 'lrby3', 'lrgg3'])
fbrb3, fbby3, fbgg3 = (mgr.bddVar(None, nm)
                       for nm in ['fbrb3', 'fbby3', 'fbgg3'])

lrrg4, lrby4, lrgy4 = (mgr.bddVar(None, nm)
                       for nm in ['lrrg4', 'lrby4', 'lrgy4'])
fbrg4, fbby4, fbgy4 = (mgr.bddVar(None, nm)
                       for nm in ['fbrg4', 'fbby4', 'fbgy4'])

# A pair of faces of a cube that is used for the left-right faces of the
# stack may not be used for the front-back faces.  Note that no cube has
# two pairs of faces with the same colors.
C = ~((lrrr1 & fbrr1) | (lrrg1 & fbrg1) | (lrby1 & fbby1))
C &= ~((lrrb2 & fbrb2) | (lrry2 & fbry2) | (lrgy2 & fbgy2))
C &= ~((lrrb3 & fbrb3) | (lrby3 & fbby3) | (lrgg3 & fbgg3))
C &= ~((lrrg4 & fbrg4) | (lrby4 & fbby4) | (lrgy4 & fbgy4))

# For each cube, exactly one pair of opposing faces must show on the
# left-right faces of the stack and one pair must show on the front-back
# faces of the stack.
C &= mgr.cardinality([lrrr1, lrrg1, lrby1], 1)
C &= mgr.cardinality([fbrr1, fbrg1, fbby1], 1)
C &= mgr.cardinality([lrrb2, lrry2, lrgy2], 1)
C &= mgr.cardinality([fbrb2, fbry2, fbgy2], 1)
C &= mgr.cardinality([lrrb3, lrby3, lrgg3], 1)
C &= mgr.cardinality([fbrb3, fbby3, fbgg3], 1)
C &= mgr.cardinality([lrrg4, lrby4, lrgy4], 1)
C &= mgr.cardinality([fbrg4, fbby4, fbgy4], 1)

# Each color must appear exactly once on each of the large faces of the stack.
C &= ((lrrr1 & ~lrrg1 & ~lrrb2 & ~lrrb3 & ~lrrg4) |
      (~lrrr1 & mgr.cardinality([lrrg1, lrrb2, lrry2, lrrb3, lrrg4], 2)))
C &=  ((fbrr1 & ~fbrg1 & ~fbrb2 & ~fbrb3 & ~fbrg4) |
      (~fbrr1 & mgr.cardinality([fbrg1, fbrb2, fbry2, fbrb3, fbrg4], 2)))

C &= mgr.cardinality([lrby1, lrrb2, lrrb3, lrby3, lrby4], 2)
C &= mgr.cardinality([fbby1, fbrb2, fbrb3, fbby3, fbby4], 2)

C &= mgr.cardinality([lrby1, lrry2, lrgy2, lrby3, lrby4, lrgy4], 2)
C &= mgr.cardinality([fbby1, fbry2, fbgy2, fbby3, fbby4, fbgy4], 2)

C &= ((lrgg3 & ~lrrg1 & ~lrgy2 & ~lrrg4 & ~lrgy4) |
      (~lrgg3 & mgr.cardinality([lrrg1, lrgy2, lrrg4, lrgy4], 2)))
C &= ((fbgg3 & ~fbrg1 & ~fbgy2 & ~fbrg4 & ~fbgy4) |
      (~fbgg3 & mgr.cardinality([fbrg1, fbgy2, fbrg4, fbgy4], 2)))

# Lexicographic constraint to eliminate solutions obtained by rotating
# other solutions by 90 degrees.
C &= mgr.inequality(0, [lrrr1, lrrg1, lrby1], [fbrr1, fbrg1, fbby1])

C.summary(name='C1')
print_solution(mgr, C)

"""Then we solve the puzzle for these other four cubes.

       +---+                +---+
       | Y |                | G |
   +---+---+---+---+    +---+---+---+---+
   | R | G | B | R |    | R | G | B | G |
   +---+---+---+---+    +---+---+---+---+
       | Y |                | R |
       +---+                +---+

       +---+                +---+
       | Y |                | Y |
   +---+---+---+---+    +---+---+---+---+
   | R | Y | R | B |    | R | G | R | Y |
   +---+---+---+---+    +---+---+---+---+
       | G |                | B |
       +---+                +---+
"""

# Get new manager (and dispose of old manager).
mgr = Cudd()

lrrb1, lrrg1, lryy1 = (mgr.bddVar(None, nm)
                       for nm in ['lrrb1', 'lrrg1', 'lryy1'])
fbrb1, fbrg1, fbyy1 = (mgr.bddVar(None, nm)
                       for nm in ['fbrb1', 'fbrg1', 'fbyy1'])

lrrb2, lrrg2, lrgg2 = (mgr.bddVar(None, nm)
                       for nm in ['lrrb2', 'lrrg2', 'lrgg2'])
fbrb2, fbrg2, fbgg2 = (mgr.bddVar(None, nm)
                       for nm in ['fbrb2', 'fbrg2', 'fbgg2'])

lrrr3, lrby3, lrgy3 = (mgr.bddVar(None, nm)
                       for nm in ['lrrr3', 'lrby3', 'lrgy3'])
fbrr3, fbby3, fbgy3 = (mgr.bddVar(None, nm)
                       for nm in ['fbrr3', 'fbby3', 'fbgy3'])

lrrr4, lrby4, lrgy4 = (mgr.bddVar(None, nm)
                       for nm in ['lrrr4', 'lrby4', 'lrgy4'])
fbrr4, fbby4, fbgy4 = (mgr.bddVar(None, nm)
                       for nm in ['fbrr4', 'fbby4', 'fbgy4'])

# A pair of faces of a cube that is used for the left-right faces of the
# stack may not be used for the front-back faces.  Note that no cube has
# two pairs of faces with the same colors.
C = ~((lrrb1 & fbrb1) | (lrrg1 & fbrg1) | (lryy1 & fbyy1))
C &= ~((lrrb2 & fbrb2) | (lrrg2 & fbrg2) | (lrgg2 & fbgg2))
C &= ~((lrrr3 & fbrr3) | (lrby3 & fbby3) | (lrgy3 & fbgy3))
C &= ~((lrrr4 & fbrr4) | (lrby4 & fbby4) | (lrgy4 & fbgy4))

# For each cube, exactly one pair of opposing faces must show on the
# left-right faces of the stack and one pair must show on the front-back
# faces of the stack.
C &= mgr.cardinality([lrrb1, lrrg1, lryy1], 1)
C &= mgr.cardinality([fbrb1, fbrg1, fbyy1], 1)
C &= mgr.cardinality([lrrb2, lrrg2, lrgg2], 1)
C &= mgr.cardinality([fbrb2, fbrg2, fbgg2], 1)
C &= mgr.cardinality([lrrr3, lrby3, lrgy3], 1)
C &= mgr.cardinality([fbrr3, fbby3, fbgy3], 1)
C &= mgr.cardinality([lrrr4, lrby4, lrgy4], 1)
C &= mgr.cardinality([fbrr4, fbby4, fbgy4], 1)

# Each color must appear exactly once on each of the large faces of the stack.
C &= ((lrrr3 & ~lrrb1 & ~lrrg1 & ~lrrb2 & ~lrrg2 & ~lrrr4) |
      (lrrr4 & ~lrrb1 & ~lrrg1 & ~lrrb2 & ~lrrg2 & ~lrrr3) |
      (~lrrr3 & ~lrrr4 & mgr.cardinality([lrrb1, lrrg1, lrrb2, lrrg2], 2)))
C &= ((fbrr3 & ~fbrb1 & ~fbrg1 & ~fbrb2 & ~fbrg2 & ~fbrr4) |
      (fbrr4 & ~fbrb1 & ~fbrg1 & ~fbrb2 & ~fbrg2 & ~fbrr3) |
      (~fbrr3 & ~fbrr4 & mgr.cardinality([fbrb1, fbrg1, fbrb2, fbrg2], 2)))

C &= mgr.cardinality([lrrb1, lrrb2, lrby3, lrby4], 2)
C &= mgr.cardinality([fbrb1, fbrb2, fbby3, fbby4], 2)

C &= ((lryy1 & ~lrby3 & ~lrgy3 & ~lrby4 & ~lrgy4) |
      (~lryy1 & mgr.cardinality([lrby3, lrgy3, lrby4, lrgy4], 2)))
C &= ((fbyy1 & ~fbby3 & ~fbgy3 & ~fbby4 & ~fbgy4) |
      (~fbyy1 & mgr.cardinality([fbby3, fbgy3, fbby4, fbgy4], 2)))

C &= ((lrgg2 & ~lrrg1 & ~lrrg2 & ~lrgy3 & ~lrgy4) |
      (~lrgg2 & mgr.cardinality([lrrg1, lrrg2, lrgy3, lrgy4], 2)))
C &= ((fbgg2 & ~fbrg1 & ~fbrg2 & ~fbgy3 & ~fbgy4) |
      (~fbgg2 & mgr.cardinality([fbrg1, fbrg2, fbgy3, fbgy4], 2)))

# Lexicographic constraint.
C &= mgr.inequality(0, [lrrb1, lrrg1, lryy1], [fbrb1, fbrg1, fbyy1])

C.summary(name='C2')
print_solution(mgr, C)
