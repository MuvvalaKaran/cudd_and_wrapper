"""Basic ZDD manipulation."""

from __future__ import print_function, unicode_literals

from cudd import Cudd
n = 4
# With ZDDs we usually pick the number of variables right away,
# because adding variables changes the semantics of existing ZDDs,
# which is rarely what we want.
m = Cudd(0,n)

# Creation of list z gives us the opportunity to name the variables.
z = [m.zddVar(i, 'z' + str(i)) for i in range(n)]

print("z[0] has index", z[0].index(), end="")
z[0].display()
print(z[0])

print("z[1] also has index", z[1].index(), end="")
z[1].display()

m.zddOne().display(name="one")

base = m.zddBase()
base.display(name="base")

empty = m.zddEmpty()
empty.display(name="empty")

f1 = base.change(3)
f1.display(name="change z[3]")

f2 = base.change(2)
f2.display(name="change z[2]")

m.dumpDot([f2],['F2'])

f3 = z[0].ite(z[1], z[3])
f3.display(name="ite")

f4 = f1 | f2
f4.display(name="union")

f5 = ~f4
f5.display(name="negation")

f6 = f5 & f3
f6.display(name="intersection")

f7 = f6.subset0(0)
f7.display(name="subset0")

f8 = f6.subset1(2)
f8.display(name="subset1")

f9 = z[0] ^ z[2]
f9.display(name="xor")

f10 = z[2].iff(z[1])
f10.display(name="iff")

# Make sure we have the BDD variables before conversion.
x = [m.bddVar(i, 'x' + str(i)) for i in range(n)]
b = f3.toBDD()
b.display(name="toBDD")

print("back-and-forth preserves function:", b.toZDD() == f3)

print("support:", f3.support())
