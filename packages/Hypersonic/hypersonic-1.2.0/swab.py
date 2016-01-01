#!/usr/bin/env python

import sys

ifile = open(sys.argv[1])
ofile = open(sys.argv[2],"w")
while 1:
  s = ifile.read(2)
  if not s:
    break
  s = s[1]+s[0]
  ofile.write(s)

  
