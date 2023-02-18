"""Test ZDD reordering functions."""

from __future__ import print_function

from cudd import Cudd, REORDER_SIFT_CONVERGE
m = Cudd(0,6)
m.enableReorderingReporting()
a,b,c,d,e,f = (m.zddVar(i, chr(ord('a') + i)) for i in range(6))
f = a & c & e | b & d & f
f.display(name='f')
m.zddReduceHeap()
f.display(name='f')
print("reordering reporting is", "enabled" if m.reorderingReporting() else "disabled")
(status,method) = m.reorderingStatusZdd()
print("reordering with method", method, "is", "enabled" if status else "disabled")
m.disableReorderingReporting()
print("reordering reporting is", "enabled" if m.reorderingReporting() else "disabled")
m.enableOrderingMonitoring()
print("ordering monitoring is", "enabled" if m.orderingMonitoring() else "disabled")
# Enabling monitoring also enables reporting.
print("reordering reporting is", "enabled" if m.reorderingReporting() else "disabled")
m.zddShuffleHeap([i for i in range(m.sizeZ())])
m.zddReduceHeap(REORDER_SIFT_CONVERGE)
