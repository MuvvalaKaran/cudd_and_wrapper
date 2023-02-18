"""Test ZDD-to-BDD order alignment."""

from __future__ import print_function

from cudd import Cudd

def testZddAlignment():
    """Test alignments of ZDDs to BDDs."""
    print("Test alignment of ZDDs to BDDs")
    m = Cudd()

    n = 4
    x = [m.bddVar(i, 'x' + str(i)) for i in range(n)]

    f = (x[0] | x[2]) & (x[1] | x[3])

    print("there are", m.sizeZ(), "ZDD variables")
    m.zddVarsFromBddVars(2)

    (h, hc) = f.isop(f, True)

    if h != f:
        raise RuntimeError("It should be f <= h <= f.")

    print("h =", h)
    h.display(name="h")
    # A prime cover of a unate function is unate.
    print("prime cover of h:")
    hc.printCover()

    # Print variable order before and after each reordering.
    m.enableOrderingMonitoring()
    m.zddRealignEnable()
    print("ZDD order:", end=" ")
    m.printZddOrder()
    print("calling reduceHeap")
    m.reduceHeap()
    print("ZDD order:", end=" ")
    # Companion variables are automatically grouped.
    m.printZddOrder()

    # Covers are affected by variable order.
    h.display(name="h")
    hc.printCover()

    m.bddRealignEnable()
    m.zddReduceHeap()

    h.display(name="h")
    hc.printCover()
    print("there are", m.sizeZ(), "ZDD variables")

def testBddAlignment():
    """Test alignment of BDDs to ZDDs."""
    print("\nTest alignment of BDDs to ZDDs")
    m = Cudd()

    n = 5
    x = [m.bddVar(i, 'x' + str(i)) for i in range(n)]

    f = x[0] & x[1] & x[2] & x[4]
    # Make a fixed variable group with the first three variables.
    m.makeTreeNode(0,3)

    print("there are", m.sizeZ(), "ZDD variables")
    m.zddVarsFromBddVars(2)

    (dummy, fc) = f.isop(f, True)

    if dummy != f:
        raise RuntimeError("ISOP returned incorrect result")

    print("f =", f)
    f.display(name="f")
    print("prime cover of f:")
    fc.printCover()

    m.enableOrderingMonitoring()
    m.bddRealignEnable()
    print("BDD order:", end=" ")
    m.printBddOrder()
    print("calling reduceHeap")
    m.zddReduceHeap()
    print("BDD order:", end=" ")
    m.printBddOrder()


testZddAlignment()
testBddAlignment()
