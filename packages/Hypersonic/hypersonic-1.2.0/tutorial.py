#!/usr/bin/env python

"""
Here are some examples to wet your appetite.
To run them, use the number as arg, eg.
$ ./tutorial.py 5
Make sure the volume is turned down first!
"""

from Sonic import *

def test00():
  # play a sin wave
  sin = Sin() # make a task
  dsp = Dsp()
  sin | dsp
  dsp.start( sin.push ) # portaudio uses callbacks
  while 1:
    #sin.push() # push signal upstream
    sleep(1)

def test01():
  f = 440.0
  sin = Sin(f)
  sin | Dsp()
  while 1:
    sin.push()
    f *= 0.99
    sin.set_f(f) # change the frequency

def test02():
  # mixing sources
  sins = [ Sin(110 + i*110, 0.2) for i in range(5) ]
  dsp = Dsp()
  add = Add()
  for sin in sins:
    sin | add
  add | dsp
  while 1:
    # a single push won't work here, so we
    # pull from downstream
    dsp.pull()

# Task objects process signals
# obtained from Buffer objects (memory)
# via Pipe objects (smart pointers).

def test03():
  sin = Sin() # a Task
  dsp = Dsp() # a Task

  # sin | dsp
  buf = Buffer() # a Buffer
  p1 = Pipe( sin, buf )  # open a Pipe
  p2 = Pipe( buf, dsp ) # another Pipe

  while 1:
    sin.push()


# pipes can be told to limit how much they read or write.
def test04():
  sin1 = Sin(110)
  sin2 = Sin(220)
  dsp = Dsp()
  buf = Buffer()

  # a utility function (!alias pipe)
  # that makes pipes between tasks and buffers:
  p1, p2 = connect( sin1, buf, dsp )

  p1.rlimit( 4096 )
  # ! this uses a bytecount:
  # ! each (mono) sample is 2 bytes (a short)
  # ! so we will get 2048 samples, at 44100 samples/second
  # ! this is about 1/20th second

  null_log() # turn off logging
  while 1:
    while not p1.done():
      dsp.pull()
    p1.close()
    p1 = Pipe( sin2, buf ) # new Pipe
    p1.rlimit( 4096 )
    while not p1.done():
      dsp.pull()
    p1.close()
    p1 = Pipe( sin1, buf )
    p1.rlimit( 4096 )
  # blech, sounds terrible ..

# Most of the tasks deal with short int (2 byte) sample data (no floats!).

def test05():
  sources = [ Sin(110), Sin(220) ]
  # You could add more oscillators, eg. Tri() or Squ().

  # Use a linear envelope to smooth the changes between sources
  w = 128  # smoothing width
  W = 4096 # total width
  env = Linear(
    # these are linear control points: (width, level) pairs
    ((w, 1<<14), (W-2*w, 1<<14), (w, 0)) )
  # ! Because Linear objects are arithmetic they
  # ! deal with sample size, which equals bytecount/2

  ebuf = Buffer() # envelope buffer
  rmod = RMod() # this will multiply it's inputs
  dsp = Dsp()
  connect( env, ebuf, rmod )
  rmod | dsp
  sbuf = Buffer() # signal buffer
  p = Pipe( sources[0], sbuf )
  Pipe( sbuf, rmod )
  # draw a picture :)

  p.rlimit(W*2) # ! bytecount

  null_log() # turn off logging
  i = 0
  while 1:
    while not p.done():
      dsp.pull()

    # check all buffers are empty
    while dsp.pull():
      pass

    p.close()
    i += 1
    p = Pipe( sources[i%len(sources)], sbuf )
    p.rlimit(W*2) # ! bytecount
  # sounds better, huh?

# Connected objects (pipes, bufs, tasks) all
# reference each other, so we only need to hold
# a reference to one of them to keep them from being
# garbage collected.

def test06():
  # FIXME: files need to be in raw (cdr) format.
  # use eg. sox to convert from/to wav,aif etc:
  # $ sox mysound.wav mysound.raw
  # $ sox -r 44100 -w -s -c 1 mysound.raw mysound.wav
  print " *** WARNING: On OSX and PPC platforms you may need to use ./swab.py to swap the byte order of sample.raw. *** "
  null_log()
  ifile = FileRd( "sample.raw" ) # a file reading task
  dsp = Dsp()
  ifile | dsp
  while not ifile.done():
    ifile.push()

def test07():
  sources = [ Sin( 60+80*i, 0.3**i ) for i in range(4) ] +\
    [ Tri( 60+81*i, 0.3**i ) for i in range(4) ]
  mix = Mix(0.7)
  dsp = Dsp()
  dsp( mix( *sources )) # connect using the call notation
  while 1:
    dsp.pull()

# a stereo test
def test08():
  left = Mix()(*[ Sin( 60+80*i, 0.3**i ) for i in range(4) ])
  right = Mix()(*[ Sin( 40+81*i, 0.3**i ) for i in range(4) ])
  dsp = Dsp(stereo=1)
  dsp( Interleave()(left, right) )
  while 1:
    dsp.pull()

# SDL test
def test09():
  dsp = Dsp( mode="r" ) # read from the soundcard
  dsp | Trace() # make an oscilloscope window
  while 1:
    dsp.push()

if __name__ == "__main__":
  try:
    i = int(sys.argv[1])
    exec "test%.2d()"%i
  except IndexError:
    i = 0
    print __doc__




