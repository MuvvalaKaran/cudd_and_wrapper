"""Tournament puzzle.  A complete graph is oriented by Alice and Bob
   according to the following rules:

   - Alice orients one edge.
   - Bob orients from 1 to b edges.

   This repeats until the graph is turned into a tournament (all edges
   are oriented).
   Alice wins if a cycle results in the process; otherwise Bob wins.
"""

from __future__ import print_function, unicode_literals, division
import random
import graphviz as gv
import argparse
from functools import reduce
from cudd import Cudd

def pre(TR, From):
    """Compute the predecessors of From according to TR."""
    fromY = From.swapVariables(xv, yv)
    return TR.andAbstract(fromY, ycube)

def img(TR, From):
    """Compute the successors of From according to TR."""
    return TR.andAbstract(From, xcube).swapVariables(xv, yv)

def onedir(u,v):
    """Return the mutual exclusion constraint for the variables."""
    if len(u) != len(v):
        raise RuntimeError('variable lists of different length')
    mutex = mgr.bddOne()
    for i in range(len(u)):
        mutex &= ~(u[i] & v[i])
    return mutex

def complete(u,v):
    """Return the completeness constraint for the variables."""
    if len(u) != len(v):
        raise RuntimeError('variable lists of different length')
    compl = mgr.bddOne()
    for i in range(len(u)):
        compl &= u[i] ^ v[i]
    return compl

def monotone(u,v):
    """Return the monotonicity condition for transition relations."""
    if len(u) != len(v):
        raise RuntimeError('variable lists of different length')
    mono = mgr.bddOne()
    for i in range(len(u)):
        mono &= ~u[i] | v[i]
    return mono

def cardinalitydifference(u, v, lb, ub=None):
    """Return the BDD for lb <= |u| - |v| <= ub."""
    if len(u) != len(v):
        raise RuntimeError('variable lists of different length')
    if ub is None:
        ub = lb
    adict = {i: mgr.bddOne() for i in range(lb,ub+1)}
    clb = lb
    cub = ub
    nv = len(u)
    for i in range(nv-1, -1, -1):
        bdict = {}
        for j in range(clb, cub+2):
            vpos = adict[j-1] if j-1 in adict else mgr.bddZero()
            vneg = adict[j] if j in adict else mgr.bddZero()
            vij = v[i].ite(vpos,vneg)
            bdict[j] = vij
        clb = max(clb - 1, -i)
        cub = min(cub + 1, i)
        adict = {}
        for j in range(clb, cub+1):
            upos = bdict[j+1] if j+1 in bdict else mgr.bddZero()
            uneg = bdict[j] if j in bdict else mgr.bddZero()
            uij = u[i].ite(upos,uneg)
            adict[j] = uij
    return adict[0]

def build_init():
    """Build initial state."""

    fixed = mgr.bddOne()
    init = ~xt if args.first == 'Bob' else xt
    if not args.initial:
        # W.l.o.g. we assume that Alice has oriented the edge between 0 and 1.
        init &= xf[index(0,1)] & ~xb[index(0,1)]
        for i in range(n-1):
            for j in range(i+1,n):
                if i != 0 or j != 1:
                    init &= ~(xf[index(i,j)] | xb[index(i,j)])
    else:
        initial_list = list(args.initial)
        # Syntax check.
        if not set(initial_list) <= set(['f', 'F', 'b', 'B', '-']):
            raise RuntimeError("only 'f', 'F', 'b', 'B', and '-' are allowed in the initial string")
        if len(initial_list) != n * (n-1) // 2:
            raise RuntimeError("wrong length of initial string: " +
                               str(len(initial_list)) + " instead of " +
                               str(n * (n-1) // 2))
        for i in range(n-1):
            for j in range(i+1,n):
                k = index(i,j)
                if initial_list[k] == 'f' or initial_list[k] == 'F':
                    fixed &= xf[k] & ~xb[k]
                elif initial_list[k] == 'b' or initial_list[k] == 'B':
                    fixed &= ~xf[k] & xb[k]
                else:
                    init &= ~(xf[k] | xb[k])
        init &= fixed

    if args.verbose > 0:
        init.summary(len(x), name='init')
        fixed.summary(len(x), name='fixed')
    return (init, fixed)

def index(i,j):
    """Compute position of (i,j) block of variables in order."""
    return i*(n-1) - i*(i+1) // 2 + j - 1

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve tournament puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--nodes", help="number of nodes of the complete graph",
                    type=int, default=8)
parser.add_argument("-b", "--bob_edges", help="number of edges Bob can orient",
                    type=int, default=5)
parser.add_argument("-f", "--first", help="who moves first",
                    default="Bob")
parser.add_argument("-m", "--memory", help="target maximum memory",
                    type=int, default=8000000000)
parser.add_argument("-c", "--complete", help="complete target states",
                    action="store_true", default=False)
parser.add_argument("-r", "--reorder", help="enable dynamic variable reordering",
                    default=False, action="store_true")
parser.add_argument('-d', '--doublecheck', help='double check winning strategy',
                    default=False, action='store_true')
parser.add_argument('-s', '--seed', help='re-seed random number generator',
                    default=False, action='store_true')
parser.add_argument("-g", "--graphviz", help="display with graphviz",
                    action="store_true", default=False)
parser.add_argument("-i", "--initial", help="select initial configuration",
                    default=None)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)

args = parser.parse_args()

if args.verbose > 0:
    print([(arg, getattr(args, arg)) for arg in vars(args)])

n = args.nodes
b = args.bob_edges

mgr = Cudd(bddVars=2+2*n*(n-1), maxMem=args.memory)

# A turn variable plus two current state variables and two next state
# variables for each edge of the graph.
xt = mgr.bddVar(0, 'xt')
yt = mgr.bddVar(1, 'yt')
xf = [mgr.bddVar(4*index(i,j)+2, 'xf%d_%d' % (i,j))
      for i in range(n-1) for j in range(n) if j > i]
yf = [mgr.bddVar(4*index(i,j)+3, 'yf%d_%d' % (i,j))
      for i in range(n-1) for j in range(n) if j > i]
xb = [mgr.bddVar(4*index(i,j)+4, 'xb%d_%d' % (i,j))
      for i in range(n-1) for j in range(n) if j > i]
yb = [mgr.bddVar(4*index(i,j)+5, 'yb%d_%d' % (i,j))
      for i in range(n-1) for j in range(n) if j > i]

# All current and next state edge variables.
x = [v for pair in zip(xf, xb) for v in pair]
y = [v for pair in zip(yf, yb) for v in pair]

# All current and next state variables.
xv = [xt] + x
yv = [yt] + y

# Reordering does not seem to be effective in this problem...
if args.reorder:
    mgr.makeTreeNode(0, 2)
    for i in range(2, mgr.size(), 4):
        mgr.makeTreeNode(i, 4)
    mgr.autodynEnable()
    if args.verbose > 0:
        mgr.enableOrderingMonitoring()
    else:
        mgr.enableReorderingReporting()

# Seed random number generator from the current time.  Random numbers are
# used in picking minterms from images when producing the sample play.
if args.seed:
    random.seed()
    mgr.srandom(random.randint(1,1000))

# Build initial state.
(init, fixed) = build_init()

# Build transition relations for Alice and Bob.

# Edges may have at most one direction.
xmutex = onedir(xf,xb)
ymutex = onedir(yf,yb)
if args.verbose > 0:
    xmutex.summary(len(x), name='xmutex')
    ymutex.summary(len(x), name='ymutex')

# The transition relations are monotone: once an edge is given a direction,
# it keeps it until the end.
monot = monotone(x,y)
monotex = monot & xmutex & ymutex
if args.verbose > 0:
    monotex.summary(name='monotex')

# When xt is true (false), it's Alice's (Bob's) turn to play.
tra = xt & ~yt & cardinalitydifference(y, x, 1) & monotex & fixed
trb = ~xt & yt & cardinalitydifference(y, x, 1, b) & monotex & fixed
if args.verbose > 0:
    tra.summary(name='tra')
    if args.verbose > 2: tra.printCover()
    trb.summary(name='trb')
    if args.verbose > 2: trb.printCover()    

if args.graphviz and args.verbose > 1:
    mgr.dumpDot([tra], ['tra'], file_path='tra.dot')
    gv.Source.from_file('tra.dot').view()
    mgr.dumpDot([trb], ['trb'], file_path='trb.dot')
    gv.Source.from_file('trb.dot').view()

# Build target states: those graphs that contain at least one triangle.
# If n is the number of nodes and e is the number of edges there are
# 2^e - n! such complete graphs.  By default, though, we build the set
# possibly incomplete graphs that contain at least one triangle.
# The target graphs may be reached by either Alice or Bob.  Hence the
# turn variable is not included: there are effectively two copies of each.
compl = complete(xf, xb)
triangles = mgr.bddZero()
for i in range(n-2):
    for j in range(i+1,n-1):
        temp = mgr.bddZero()
        for k in range(j+1,n):
            temp |= (xf[index(i,j)] & xf[index(j,k)] & xb[index(i,k)]
                     | xb[index(i,j)] & xb[index(j,k)] & xf[index(i,k)])
        if args.complete:
            triangles |= temp & compl & fixed
        else:
            triangles |= temp & xmutex & fixed
if args.verbose > 0:
    triangles.summary(len(x), name='triangles')
if args.graphviz and args.verbose > 1:
    mgr.dumpDot([triangles], ['tri'], file_path='triangles.dot')
    gv.Source.from_file('triangles.dot').view()

# Solve game.
ycube = yt & reduce(lambda p, q: p & q, y)
Z = New = triangles
found = False
i = 1
while New:
    if i % 2 == 1:
        Pre = pre(tra, Z)
    else:
        Pre = pre(trb, Z) & ~pre(trb, ~Z)
    New = Pre & ~Z
    if args.verbose > 2:
        New.summary(len(x), name='New%d' % i)
        New.printCover()
    Z |= New
    if args.verbose > 0:
        Z.summary(len(x), name='Z%d' % i)
        if args.verbose > 2: Z.printCover()
    if init <= Z:
        found = True
        break
    i += 1

Zinf = Z

# Compute witness path by forward reachability analysis.
xcube = xt & reduce(lambda p, q: p & q, x)
state = init
cubes = [state.cube()[2::2]]
parity = 1 if args.first == 'Bob' else 0
print('game won by',  'Alice' if found else 'Bob')
print(''.join([str(c) for c in cubes[0]]))
if found:
    while not state <= triangles:
        To = img(trb if len(cubes) % 2 == parity else tra, state) & Zinf
        if not To:
            raise RuntimeError('empty image')
        state = To.pickOneMinterm(xv)
        cubes.append(state.cube()[2::2])
        print(''.join([str(c) for c in cubes[-1]]))
else:
    safeset = ~Zinf & xmutex
    while not state <= compl:
        if len(cubes) % 2 == parity:
            To = img(trb, state) & safeset
        else:
            To = img(tra, state)
            if not To <= safeset:
                raise RuntimeError('Alice escaped safe set')
        if not To:
            raise RuntimeError('empty image')
        state = To.pickOneMinterm(xv)
        cubes.append(state.cube()[2::2])
        print(''.join([str(c) for c in cubes[-1]]))

# Visualize witness path.
dot = gv.Digraph(comment='Sample play')

for i in range(n):
    dot.node(str(i), 'N%d' % i)

if not args.initial:
    dot.edge('0', '1', style='solid', label=' 0')
else:
    initial_list = list(args.initial)
    for i in range(n-1):
        for j in range(i+1,n):
            k = index(i,j)
            if initial_list[k] == 'f':
                dot.edge(str(i), str(j), style='solid', label=' i')
            elif initial_list[k] == 'F':
                dot.edge(str(i), str(j), style='dashed', label=' i')
            elif initial_list[k] == 'b':
                dot.edge(str(j), str(i), style='solid', label=' i')
            elif initial_list[k] == 'B':
                dot.edge(str(j), str(i), style='dashed', label=' i')

for m in range(1,len(cubes)):
    estyle = 'dashed' if m % 2 == parity else 'solid'
    for i in range(n-1):
        for j in range(i+1,n):
            k = index(i,j)
            fslice = cubes[m][2*k:2*(k+1)]
            if fslice == cubes[m-1][2*k:2*(k+1)]:
                continue
            if fslice == [0, 1]:
                dot.edge(str(j), str(i), style=estyle, label=' '+str(m))
            elif fslice == [1, 0]:
                dot.edge(str(i), str(j), style=estyle, label=' '+str(m))

dot.render('sample-play.dot', view=args.graphviz)

if args.doublecheck:
    if found:
        # Check that Bob cannot escape Alice's winning region.
        print('Checking that Bob cannot stop Alice from creating a cycle...')
        if img(trb, Zinf) <= Zinf:
            print(' done')
        else:
            raise RuntimeError("Bob escaped Alice's winning region")
    else:
        # Check that Alice cannot escape Bob's winning region.
        print('Checking that Bob can stop Alice from creating a cycle...')
        if img(tra, safeset) <= safeset:
            print(' done.')
        else:
            raise RuntimeError('Alice escaped safe set')
