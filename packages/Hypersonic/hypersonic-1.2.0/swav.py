#!/usr/bin/env python

import os, sys

name = sys.argv[1]
assert name.endswith(".raw")
name = name[:-4]

cmd = "sox -r 44100 -w -s -c 1 %s.raw %s.wav"%(name,name)
print cmd
os.system( cmd )

cmd = "sweep %s.wav"%name
print cmd
os.system( cmd )

cmd = "rm %s.wav"%name
print cmd
os.system( cmd )
