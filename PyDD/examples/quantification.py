"""Examples of quantification."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()

# Create variables a, b, c, d with names 'a', 'b', 'c', 'd'.
a,b,c,d = (m.bddVar(i, chr(ord('a') + i)) for i in range(4))

f = a & ~b | c & ~d
print("f =", f)
# f = ~(a & (b & (d | ~c)) | ~a & (d | ~c))

print("Exists a . f =", f.existAbstract(a))
# Exists a . f = ~(b & (d | ~c)

print("Forall c&d . f =", f.univAbstract(c&d))
# Forall c&d . f = ~(b | ~a)

g = b | ~c & ~d
print(f.andAbstract(g, b&c) == (f&g).existAbstract(b&c))
# True
