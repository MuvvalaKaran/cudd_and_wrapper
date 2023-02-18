"""Test timing-related functions."""

from __future__ import print_function

from cudd import Cudd

m = Cudd()

N = 40
m.reserve(N)

x = [m.bddVar(i, 'x' + str(i)) for i in range(N)]

print("Manager start time:", m.readStartTime(), "ms")

# Give the manager 20 ms.
m.setTimeLimit(m.readElapsedTime() + 10) # time limit in ms
m.increaseTimeLimit(10)
print("The manager is currently time-", "limited" if m.timeLimited() else "unlimited", sep="")

# Try to build a large BDD.
try:
    f = m.bddOne()
    for i in range(N//2):
        f &= x[i] | x[i+N//2]
    print("f", end="")
    f.summary()
except MemoryError as e:
    print("Exception:", m.readErrorCode())
    print("Elapsed time:", m.readElapsedTime(), "ms")
    print("Time limit was:", m.readTimeLimit(), "ms")
    m.clearErrorCode()
    print("After clearing error code, manager says:", m.readErrorCode())

m.unsetTimeLimit()
print("Current time limit:", m.readTimeLimit(), "ms")
print("The manager is currently time-", "limited" if m.timeLimited() else "unlimited", sep="")
