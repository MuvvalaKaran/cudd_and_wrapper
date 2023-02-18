"""Example of prime and cube generation."""

from __future__ import print_function

def convert(x):
    return "-" if x == 2 else str(x)

def list_to_string(prime):
    return "".join(map(convert, prime))

from cudd import Cudd
m = Cudd()

a,b,c,d = (m.bddVar(i, chr(ord('a') + i)) for i in range(4))
f = a & ~b | c & ~d
print(f)
# ~(a & (b & (d | ~c)) | ~a & (d | ~c))

print("BDD primes")
for prime in f.generate_primes():
    print(list_to_string(prime))
# 10--
# --10

print("BDD cubes")
for cube in f.generate_cubes():
    print(list_to_string(cube))
# 0-10
# 10--
# 1110

print("ADD cubes")
g = f.toADD() + m.addConst(2.0)
for cube in g.generate_cubes():
    print(list_to_string(cube[0]), "{:g}".format(cube[1]))
# 0-0- 2
# 0-10 3
# 0-11 2
# 10-- 3
# 110- 2
# 1110 3
# 1111 2
