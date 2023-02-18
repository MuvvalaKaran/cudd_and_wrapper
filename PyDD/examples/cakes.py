""" Compute cake classifier according to John's tastes (from Kubat's book).

The five attributes and their values are:

  shape         : circle triangle square
  crust-size    : thick thin
  crust-shade   : gray white dark
  filling-size  : thick thin
  filling-shade : gray white dark
  class         : pos

100 10 100 10 001 1 : circle   thick, gray crust  thick, dark filling  pos
100 10 010 10 001 1 : circle   thick, white crust thick, dark filling  pos
010 10 001 10 100 1 : triangle thick, dark crust  thick, gray filling  pos
100 01 010 01 001 1 : circle   thin, white crust  thin, dark filling   pos
001 10 001 01 010 1 : square   thick, dark crust  thin, white filling  pos
100 10 010 01 001 1 : circle   thick, white crust thin, dark filling   pos
100 10 100 10 010 0 : circle   thick, gray crust  thick, white filling neg
001 10 010 10 100 0 : square   thick, white crust thick, gray filling  neg
010 01 100 01 001 0 : triangle thin, gray crust   thin, dark filling   neg
100 10 001 10 010 0 : circle   thick, dark crust  thick, white filling neg
001 10 010 10 001 0 : square   thick, white crust thick, dark filling  neg
010 10 010 10 100 0 : triangle thick, white crust thick, gray filling  neg

"""

from __future__ import print_function
from cudd import Cudd, REORDER_GENETIC

def convert(x):
    """ Convert integers to characters."""
    return "-" if x == 2 else str(x)

def list_to_string(prime):
    """Join list elements into string. """
    return "".join(map(convert, prime))

def strings_to_bdd(strings):
    """ Convert a list of positional cubes to the BDD for their disjunction."""
    b = mgr.bddZero()
    for cube in strings:
        b |= mgr.fromCubeString(cube.replace(" ", ""))
    return b

# Initalize manager and variables.
varnames = ['circle', 'triangle', 'square',
            'thick_crust', 'thin_crust',
            'gray_crust', 'white_crust', 'dark_crust',
            'thick_filling', 'thin_filling',
            'gray_filling', 'white_filling', 'dark_filling']
mgr = Cudd()
mgr.enableOrderingMonitoring()
X = [mgr.bddVar(i, varnames[i]) for i in range(len(varnames))]

# Build on-set and off-set.
on_set = ["100 10 100 10 001",
          "100 10 010 10 001",
          "010 10 001 10 100",
          "100 01 010 01 001",
          "001 10 001 01 010",
          "100 10 010 01 001"]

f = strings_to_bdd(on_set)

off_set = ["100 10 100 10 010",
           "001 10 010 10 100",
           "010 01 100 01 001",
           "100 10 001 10 010",
           "001 10 010 10 001",
           "010 10 010 10 100"]

r = strings_to_bdd(off_set)

# Look for a better order.  Ordering affects the quality of the covers.
mgr.reduceHeap(REORDER_GENETIC)

f.summary(name='f')

print('********** Using BDDs ***********')
fp = mgr.bddZero()
for prime in f.generate_primes(~r):
    cubestring = list_to_string(prime)
    print(cubestring)
    fp |= mgr.fromCubeString(cubestring)

fp.display(name='fp', detail=4)

print('********** Using ZDDs ***********')
mgr.zddVarsFromBddVars(2)
mgr.zddRealignEnable()
(fb, fz) = f.isop(~r, True)
fb.summary(name='fb')
fz.printCover()

print('fp equals fb        :', fp == fb)

print('********** factored form ***********')
mgr.reduceHeap(REORDER_GENETIC)
print('good cakes:', fp)

# For the best classifier to emerge, we need two clusters:
# examples 1,2,4,6 and examples 3,5.  Therefore a good cover
# must contain the supercubes of the two clusters.
supercubes = ["0-- 10 001 -- --0",
              "100 -- --0 -- 001"]

h = strings_to_bdd(supercubes)

print('\nh is disjoint from r:', h <= ~r)
print('h implies fb        :', h <= fb)
