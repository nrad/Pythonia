#!/usr/bin/env python

import sys
from time import *
from Sonic import *

buf=Buffer()
op=None
stereo = sys.argv[1].endswith(".st.raw")
#stereo=1
skip = 0
count = 0
options = [ s for s in sys.argv[1:] if s.count('=') ]
for s in options:
  print "exec",s
  exec s
filenames = [ s for s in sys.argv[1:] if not s.count('=') ]
#print filenames
  
dsp=DspWr(stereo=stereo)
op=pipe(buf,dsp)
for filename in filenames:
  t=FileRd(filename)
  if skip:
    t.seek(skip)
  if count:
    op.rlimit(count)
  p=t.open_writer(buf)
  while not op.done():
    dsp.pull()
    t.push()
    if t.done():
      break
  t.close_writer(p)
  del t
  gc.collect()
  free_garbage()
  sleep(0.4)

