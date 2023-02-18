"""Display a BDD in various ways."""

from __future__ import print_function, unicode_literals
from cudd import Cudd 

def show():
    """Show function in several ways."""
    f.display(detail=4, name='f')
    print(f)
    f.printCover()

mgr = Cudd()

a,b,c,d,e = [mgr.bddVar(i, chr(ord('a') + i)) for i in range(5)]

f = ((a & b & c & d & ~e) | (a & b & ~c & ~e) | (a & ~b) |
     (~a & b & c & d & ~e) | (~a & b & ~c & ~e) | (~a & ~b))

print('First with variable order a < b < c < d < e')
show()

# Choose a slightly better order.
mgr.shuffleHeap([0, 1, 4, 2, 3])
print('Now with variable order a < b < e < c < d')
show()
