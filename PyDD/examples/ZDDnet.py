"""Network encoding with ZDDs.

   The network has four vertices: s, a, b, t 
   and five edges: 
     e1: {s,a}, e2: {s,b}, e3: {a,b}, e4: {a,t}, e5: {b,t}.
"""

from __future__ import print_function
from cudd import Cudd

# Create manager with 5 ZDD variables.
n=5
m=Cudd(0,n)

# Name the variables: one for each edge.
e = [m.zddVar(i, 'e' + str(i+1)) for i in range(n)]
# Print variable order.
print(' '.join((m.getZVariableName(i) for i in range(n))))

for i in range(m.sizeZ()):
    print('index', i, 'corresponds to edge', m.getZVariableName(i))

base = m.zddBase()
# Simple paths from s to t.  p1 uses e1, e3, and e5; and so on.
p1 = base.change(0).change(2).change(4)
p2 = base.change(0).change(3)
p3 = base.change(1).change(2).change(3)
p4 = base.change(1).change(4)
f = p1 | p2 | p3 | p4
f.display(name='f')
m.dumpDot([f],['f'])

# Changes may be factored.
g = (base.change(2).change(4) | base.change(3)).change(0)
g |= (base.change(2).change(3) | base.change(4)).change(1)

print('f and g are', ('equal' if f == g else 'different'))
