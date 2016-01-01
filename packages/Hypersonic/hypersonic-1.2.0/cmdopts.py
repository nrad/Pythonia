#!/usr/bin/env python

import sys

def getopts():
  return [ opt for opt in sys.argv[1:] if opt.count("=") ]
getcmds = getopts

def getelse():
  return [ opt for opt in sys.argv[1:] if not opt.count("=") ]
getfiles = getelse

#def execopts(loc,glo):
  #print "execopts",loc,glo
  #opts = getopts()
  #for opt in opts:
    ##exec( opt, loc, glo )
    #opt = opt.split("=")
    #loc[ opt[0] ] = eval( opt[1] )
  #print loc,glo

def test():
  a = 1
  b = 10
  print "a = ",a
  print "b = ",b
  print "opts = ",getopts()
  print "else = ",getelse()
  for opt in getopts():
    exec opt
  print "a = ",a
  print "b = ",b

if __name__=="__main__":
  test()
