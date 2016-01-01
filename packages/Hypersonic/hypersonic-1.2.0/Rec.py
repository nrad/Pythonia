#!/usr/bin/env python

import sys
from time import *
from Sonic import *

def rec(filename,stereo=0):
  t=FileWr(filename)
  buf=Buffer(4096)
  #dsp=DspRd(stereo=stereo, chn = OSS_defs.SOUND_MIXER_MIC )
  dsp=DspRd(stereo=stereo, chn = OSS_defs.SOUND_MIXER_LINE )
  pipe(dsp,buf,t)
  while 1:
  #for i in range(128):
    if dsp.push() + dsp.push() + dsp.push() == 0:
      break
    #print t.send(), dsp.send()

if __name__=="__main__":
  filename=sys.argv[1]
  stereo = filename.endswith(".st.raw")
  rec(filename,stereo)


