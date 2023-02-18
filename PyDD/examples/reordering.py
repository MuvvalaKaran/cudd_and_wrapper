"""Example of reordering."""

from __future__ import print_function

from cudd import Cudd, REORDER_GENETIC, REORDER_SIFT_CONVERGE
m = Cudd()
m.enableReorderingReporting()
a,b,c,d,e,f = (m.bddVar(i) for i in range(6))
f = a & c & e | b & d & f
f.display()
m.reduceHeap()
print("reordering reporting is", "enabled" if m.reorderingReporting() else "disabled")
m.disableReorderingReporting()
print("reordering reporting is", "enabled" if m.reorderingReporting() else "disabled")
m.enableOrderingMonitoring()
print("ordering monitoring is", "enabled" if m.orderingMonitoring() else "disabled")
# Enabling monitoring also enables reporting.
print("reordering reporting is", "enabled" if m.reorderingReporting() else "disabled")
m.reduceHeap(REORDER_GENETIC)
(status,method) = m.reorderingStatus()
print("reordering with method", method, "is", "enabled" if status else "disabled")
f.display()
# Reset order and then sift again, this time to convergence.
m.shuffleHeap(range(m.size()))
m.reduceHeap(REORDER_SIFT_CONVERGE)
