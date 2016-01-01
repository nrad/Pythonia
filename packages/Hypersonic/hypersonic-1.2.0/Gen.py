#!/usr/bin/env python

import sys
from time import *
from Sonic import *

ex = []
cmd=None
args=[]
for s in sys.argv[1:]:
  if s[0].isupper():
    if cmd:
      ex.append( cmd+str( tuple(args) ))
    args=[] # flush arguments
    cmd = s # new command
  else:
    if s[0].isdigit():
      if s.count("."):
        args.append( float(s) )
      else:
        args.append( int(s) )
    else:
      args.append( s )
if cmd:
  ex.append( cmd+str( tuple(args) ))
#print ex
#print string.join(ex,"\n")
#bomb

#tlist = [ eval(s) for s in sys.argv[1:]]
tlist=[]
for s in ex:
  print "eval('%s')"%s
  tlist.append( eval(s) )
#tlist = [ eval(s) for s in ex ]
reduce( lambda a,b:a|b, tlist )
while 1:
  count = 0
  for i in range(4):
    count+=tlist[0].push()  
  if not count: break


