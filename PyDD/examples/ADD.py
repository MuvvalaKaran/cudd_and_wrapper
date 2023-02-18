"""Basic test of ADDs."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()

n = 3
x = [m.addVar(i, 'x' + str(i)) for i in range(n)]

f = x[0].ite(x[1], m.addConst(3.0))
g = x[0].ite(x[1], x[2])

print("f", end="")
f.display(2)
print("g:", g, sep="\n")
print("to dot:")
m.dumpDot([f])

print("plus", end="")
(f + g).display(3)
print("times", end="")
(f * g).display(3)
print("minus", end="")
(f - g).display(3)
print("divide", end="")
(f / m.addConst(2.0)).display(3)
print("min", end="")
f.min(g).display(3)
print("max", end="")
f.max(g).display(3)
print("agreement", end="")
f.agreement(g).display(3)
print("negate", end="")
(-f).display(2)
print("cofactor", end="")
f.cofactor(~x[0]).display(1)
print("exist x[0]", end="")
f.existAbstract(x[0]).display(1)
print("univ x[1]", end="")
f.univAbstract(x[1]).display(1)
print("compare:", g < f)
print("log", end="")
(m.addConst(10.0)).log().display(0)
print("find min", end="")
f.findMin().display(0)
print("find max", end="")
f.findMax().display(0)

h = x[0].ite(x[1], m.addConst(1.0))
print("or", end="")
(h | g).display(3)
print("and", end="")
(h & g).display(3)
print("nand", end="")
h.nand(g).display(3)
print("nor", end="")
h.nor(g).display(3)
print("xor", end="")
h.xor(g).display(3)
print("xnor", end="")
h.xnor(g).display(3)
print("complement", end="")
(~h).display(2)

p = x[1].ite(x[0], m.addConst(1.0))
print("p", end="")
p.display(2)
p += h
print("p+h", end="")
p.display(2)
p *= m.addConst(2.0)
print("(p+h)*2", end="")
p.display(2)

print("i-th bit:", f.ithBit(0) == h)
print("compose", end="")
f.compose(x[2], 0).display(2)
print("swap", end="")
f.swapVariables(x[0:1], x[1:2]).display(2)

print("constrain", end="")
f.constrain(g).display(3)
print("restrict", end="")
f.restrict(g).display(2)

print("conversion:", f.bddThreshold(1.0))
print("conversion:", f.bddStrictThreshold(0.0).toADD() == h)
print("conversion:", f.bddPattern() == f.bddThreshold(0.5))

print("one:", m.addOne(), sep="\n")
print("zero:", m.addZero())
print("+inf:", m.plusInfinity(), sep="\n")
print("-inf:", m.minusInfinity(), sep="\n")
print("background:", m.background())
m.setBackground(m.plusInfinity())
print("background:", m.background())
m.setBackground(m.addZero())
print("background:", m.background())

# Test permutation.
perm1 = f.permute([2,1,0])
perm2 = perm1.permute([2,1,0])
if perm2 != f:
    raise RuntimeError()
try:
    perm3 = f.permute([3,2,1,0])
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))
