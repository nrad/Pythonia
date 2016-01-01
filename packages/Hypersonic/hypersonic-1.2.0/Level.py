#!/usr/bin/env python

import sys
from time import *
from Sonic import *

#null_log()
buf=Buffer(4096)
#head=Task("writeln")
head=None_()
pipe(buf,Env(),Buffer(16),head)
try:
  fnam=sys.argv[1]
  os.stat(fnam)
  t=FileRd(fnam)
except:
  t=DspRd()

p=pipe(t,buf)
while 1:
  count=0
  while head.pull():
    count+=1
    pass
  #print i
  while len(head.reader())/2:
    x=head.reader().read_short()
    #print x,
    x = 1+int( (70 * x) / (1<<15) )
    y=0; z=0
    if x<0: x=70 # overflow
    z=x==70
    if x>60: y=x-60; x=60
    print "-"*x+"="*y+" *"*z
  if t.done():
    break
t.close_writer(p)
  

