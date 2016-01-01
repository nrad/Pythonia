#!/usr/bin/python

import sys
import os
from string import *

###########################################
# recursive descent parsing
#

funcs=[]

def line_struct(line):
  #print "STRUCT ",line
  return

def line_typedef(line):
  #print "TYPEDEF ",line
  return

def line_func(line):
  global funcs
  #print "FUNC ",line
  line=replace(line,"*","* ")
  b1=find(line,"(")
  b2=find(line,")")
  sp=split(line[:b1])
  rval=join(sp[:-1])
  name=sp[-1]
  _parms=split(line[b1+1:b2],",")
  parms=[]
  for p in _parms:
    if not p: continue
    sp=split(p)
    parms.append( [join(sp[:-1]),sp[-1]] )
  funcs.append( [rval,name,parms] )
  #print "FUNC ", [rval,name,parms]
def parse_error(line):
  print "PARSE_ERROR ", line
  assert 0

def line_switch(line):
  #print "  ",line
  if count(line,"{"):
    if not count(line,"}"):
      parse_error(line)
    line_struct(line)
  elif count(line,"typedef"):
    line_typedef(line)
  else:
    if count(line,"("):
      if not count(line,")"):
        parse_error(line)
      line_func(line)
    elif count(line,"typedef"):
      line_typedef(line)
    elif count(line,"struct"):
      line_struct(line)
    else:
      #parse_error(line)
      #print "  SKIPING",line
      pass

_line=[] # accumulated
def line_semi(line):
  global _line
  if not line: return
  if line[0]=="#": return
  _line.append(line)
  if count(line,";"):
    line_switch(join(_line))
    _line=[]

__line=[] # accumulated
brace=0
def line_brace(line):
  global __line, brace
  if not line: return
  if count(line,"{"):
    brace=1
  if brace:
    __line.append(line) # accumulate
    if count(line,"}"):
      brace=0
      line_semi(join(__line))
      __line=[]
  else:
    line_semi(line)

###########################################
# pre-process then call above 
#

#sys.stderr.write( "  open pregen.h w\n" )
outf=open("pregen.h","w")
for name in sys.argv[1:]:
  f=open(name)
  while 1:
    line=f.readline()
    if not line: break
    if not count(line,"#include"): outf.write(line)
  f.close()
outf.close()

#sys.stderr.write( "  gcc -E pregen.h\n" )
f=os.popen("gcc -E pregen.h")
while 1:
  line=f.readline()
  #print "line = ",line,
  if not line: break
  assert line[-1]=='\n'
  line_brace(line[:-1])
#sys.stderr.write( "  return="+str( f.close()!=None )+"\n")

