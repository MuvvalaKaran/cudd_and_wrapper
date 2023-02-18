"""Two ways to take the conjunction of a list of BDDs."""

from __future__ import print_function
from heapq import heapify, heappush, heappop
from cudd import Cudd

def reduce_list(lst):
    """Conjoin pairs of consecutive BDDs until only one is left."""
    while len(lst) > 1:
        j = 0
        for i in range(0,len(lst)-1,2):
            lst[j] = lst[i] & lst[i+1]
            j += 1
        if len(lst) % 2 == 1:
            lst[j] = lst[-1]
            j += 1
        del lst[j:]

def heap_reduce(lst):
    """Conjoin two smallest BDDs until only one is left."""
    h = [(x.size(), x) for x in lst]
    heapify(h)
    while len(h) > 1:
        (fs,f) = heappop(h)
        (ss,s) = heappop(h)
        r = f & s
        rs = r.size()
        #print('###', fs, ss, rs, '###')
        heappush(h, (r.size(),r))
    (rets,ret) = heappop(h)
    return ret

m = Cudd()

lst = [m.bddVar() for _ in range(6)]

r = heap_reduce(lst)
print('heap', end=''); r.display()

reduce_list(lst)
print('result', end=''); lst[0].display()
