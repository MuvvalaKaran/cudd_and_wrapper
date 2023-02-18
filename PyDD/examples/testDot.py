""" Using graphviz to display a BDD.
"""
from __future__ import print_function, unicode_literals, division
import graphviz as gv
from cudd import Cudd
mgr = Cudd()
x0,x1,x2 = (mgr.bddVar(None, nm) for nm in ['x0', 'x1', 'x2'])
F = (x0 | x1) & ~x2
print(F)
G = (~x0 | ~x1) & x2
print(G)
mgr.dumpDot([F, G], ['F', 'G'], file_path='graphviztest.dot')
gv.Source.from_file('graphviztest.dot').view()
