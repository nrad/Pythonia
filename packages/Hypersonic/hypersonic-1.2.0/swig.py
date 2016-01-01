#!/usr/bin/env python

import string
import sys
from func import *

def spew():
  for rval, name, parms in funcs:
    s="%s %s(%s);"%(rval,name,
      string.join(map(lambda x:x[0]+" "+x[1],parms),","))
    if not ( name.endswith("_send") and name.startswith("task_")) \
      or name=="task_send":
      print s
    else:
      print "/* %s */"%s

print "%module sonic"
print "%{"
for file in sys.argv[1:]:
  print "#include \"%s\""%file
print "%}"
print "%include pointer.i"

spew()

