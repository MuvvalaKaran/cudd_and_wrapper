from cudd import Cudd
m = Cudd()
Q,S,U,R,V,T = (m.bddVar() for i in range(6))
F = Q & S & U | (~Q | ~S) & (R | V) | U & (R | V) | ~Q | S & T & U
G = ~Q | S & U | ~S & R | ~S & V
print(F == G)
