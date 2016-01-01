from operator import sub
def gcd(a,b):
  """Kirby's Extended Euclidean Algorithm for GCD"""
  v1 = [a,1,0]
  v2 = [b,0,1]
  while v2[0]<>0:
    p = v1[0]//v2[0]
    v2, v1 = map(sub,v1,[p*vi for vi in v2]), v2
  return v1

