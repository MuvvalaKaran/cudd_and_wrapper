"""Example of shortest-path computation by the Bellman-ford algorithm."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()
m.setBackground(m.plusInfinity())

c1,c2,c3,c4 = (m.addConst(float(i+1)) for i in range(4))

x = [m.addVar(i,   'x' + str(i)) for i in range(2)]
y = [m.addVar(i+2, 'y' + str(i)) for i in range(2)]

T = ( (~x[0] & ~x[1] &  y[0] & ~y[1] & c4)
    | (~x[0] &         ~y[0] &  y[1] & c1)
    | (~x[0] &  x[1] &  y[0] & ~y[1] & c2)
    | ( x[0] & ~x[1] &  y[0] &  y[1] & c2)
    | ( x[0] & ~x[1] & ~y[0] & ~y[1] & c4)
    | ( x[0] &  x[1] & ~y[0] & ~y[1] & c2)
    | ( x[0] &  x[1] &  y[0] & ~y[1] & c3))

# We use ~T to obtain a 0-1 ADD (as required by ITE).
T = (~T).ite(m.plusInfinity(), T)
print("T:", T, sep="\n")

start = (~x[0] & ~x[1]).ite(m.addZero(), m.plusInfinity())
distances = start

for i in range(4):
    print("iteration", i, end="")
    distances.display(2)
    w = T.triangle(distances, x).swapVariables(x,y)
    mini = distances.min(w)
    if mini == distances:
        print("converged")
        break
    distances = mini

