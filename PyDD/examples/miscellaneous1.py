"""Test the bindings of some CUDD functions."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()

# Test cofactors.

n = 4
a,b,c,d = (m.bddVar(i, chr(ord('a') + i)) for i in range(n))

f = b & (a | (c & ~d))
print("f =", f)
g = a & (b | (~c & d))

h1 = f.constrain(g)
h2 = f.restrict(g)
h3 = (f & g).squeeze(f | ~g)
h4 = f.LIcompaction(g)
h5 = f.minimize(g)
h6 = f.npAnd(g)

# All methods return b.
print("constrain:", h1)
print("restrict :", h2)
print("squeeze  :", h3)
print("LIcompact:", h4)
print("minimize :", h5)
# The non-polluting and returns a & b
print("npAnd    :", h6)

p = (a & c) | (~a & (b ^ c))
q = (a & b) | (~b & ~c)

r1 = p.constrain(q)
r2 = p.restrict(q)
r3 = (p & q).squeeze(p | ~q)
r4 = p.LIcompaction(q)
r5 = p.minimize(q)

# Constrain returns (a & b & c), restrict, LIcompaction, and
# minimize return (a & c), and squeeze returns c.
print("constrain:", r1)
print("restrict :", r2)
print("squeeze  :", r3)
print("LIcompact:", r4)
print("minimize :", r5)

# Test remapUnderApprox.
print("RUA:", f.remapUnderApprox())

# Test charToVect.
vect = f.charToVect()
print("CharToVect:")
for v in vect:
    print(v)

# Now we verify that the image of the vector is indeed f.
y = [m.bddVar(i+n, 'y' + str(i)) for i in range(n)]

T = m.bddOne()
for i in range(n):
    T &= (~y[i] ^ vect[i])

image = T.existAbstract(a&b&c&d).swapVariables(y, [a,b,c,d])
print("image:", image)
if f != image:
    raise RuntimeError()

# Test inequality and disequality.

u = m.inequality(2, y[0::2], y[1::2])
print("Inequality:", u)
uc = y[0] & ~y[1] & (y[2] | ~y[3])
if u != uc:
    raise RuntimeError()

w = m.disequality(2, y[0::2], y[1::2])
print("Disequality:", w)
wc = ~y[0] | y[1] | (y[2] ^ y[3])
if w != wc:
    raise RuntimeError()

# Test Boolean difference.

print("Boolean difference:", f.booleanDiff(a))

# Test exclusive nor.

print("Its negation:", (f.cofactor(a)).xnor(f.cofactor(~a)))

# Test checkCube.

if not (a&b&~c).isCube():
    raise RuntimeError()

if (a & (~b | c) & d).isCube():
    raise RuntimeError()

# Test conjunctive decomposition.

z = (a | b) & (c | d)
print("z:", z)
lz1,rz1 = z.genConjDecomp()
print("left:", lz1, "right:", rz1)
if (lz1 & rz1) != z:
    raise RuntimeError()
lz2,rz2 = z.varConjDecomp()
print("left:", lz2, "right:", rz2)
if (lz2 & rz2) != z:
    raise RuntimeError()
lz3,rz3 = z.approxConjDecomp()
print("left:", lz3, "right:", rz3)
if (lz3 & rz3) != z:
    raise RuntimeError()
lz4,rz4 = z.approxConjDecomp()
print("left:", lz4, "right:", rz4)
if (lz4 & rz4) != z:
    raise RuntimeError()

# Test leqUnless.

print("leqUnless:", (a | b).leqUnless(z, ~(c | d)))

# Test correlation.

print("correlation of f and g:", f.correlation(g))
print("with probabilities:", f.correlation(g, [0.6,0.3,0.4,0.8,0.5,0.5,0.5,0.5]))
try:
    print("with probabilities:", f.correlation(g, [0.6,0.3,0.4,0.8]))
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))

# Test cube and minterm selection.
print("a cube from f:", f.pickOneCube())
print("a minterm from f:", f.pickOneMinterm([a,b,c,d]))
try:
    print("another minterm from f:", f.pickOneMinterm([a,b&c,d]))
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))
print("a cube from f:", f.pickCube())

# Test shortest length.
print("shortest path of f:", f.shortestLength())
print("with costs:", f.shortestLength([1,2,3,4,1,1,1,1]))
try:
    print("with costs:", f.shortestLength([1,2,3,4]))
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))
(sp,ln) = f.shortestPath()
print("shortest path:", sp, "of length", ln)
(lcf,lnf) = f.largestCube(True)
print("largest cube of f:", lcf, "of length", lnf)
print("~g:", ~g, "largest cube of ~g:", (~g).largestCube())

# Test subsetting/supersetting.
print("HB-    :", T.subsetHeavyBranch())
print("HB-(10):", T.subsetHeavyBranch(0,10))
print("SP-    :", T.subsetShortPaths())
print("HB+    :", T.supersetHeavyBranch())
print("SP+    :", T.supersetShortPaths())

# Test permutation.
perm1 = T.permute([7,6,5,4,3,2,1,0])
perm2 = perm1.permute([7,6,5,4,3,2,1,0])
if perm2 != T:
    raise RuntimeError()
try:
    perm3 = T.permute([3,2,1,0])
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))
