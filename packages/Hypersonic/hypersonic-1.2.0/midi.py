#!/usr/bin/env python 

#from math import *
#import sys
#import string

def miditof(note):
  note -= 57.0
  return 440.0 * (2 ** ( note / 12.0 ))
def midi_scale():
  print "float\nmidi_freq[128]=\n{"
  for n in range(128):
    print "  %s,"%repr(miditof(n))
  print "};"
  
if __name__=="__main__":
  midi_scale()
