def fib(n,fstart=0):
  fibl=[fstart,fstart+1]
  for i in range(0,n):
    fibl.append(fibl[i]+fibl[i+1])
  return fibl



