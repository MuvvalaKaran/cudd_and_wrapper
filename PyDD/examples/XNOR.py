from cudd import Cudd

mgr = Cudd()

x0,x1,x2,x3 = [mgr.bddVar(name='x%s' % i) for i in range(4)]

f1 = x0.iff(x1)
f2 = x2.iff(x3)

f = f1.iff(f2)

f.display()

g = f.toADD()

g.display(detail=4)
