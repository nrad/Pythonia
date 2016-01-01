#!/usr/bin/env python

#from Sonic import *
from Quad import *

from thread import start_new_thread

try:
  import psyco
  psyco.full()
except:
  pass

class Stream:
  def __init__(self, sched):
    self.otask = None
    self._otask = None
    self.op = None
    self.obuf = None
    self.mix = Add()
    self.sched = sched
    #Zero() | Buffer() | self.mix
    #Zero() | self.mix
    self.lines = {}
    self.flag1 = 0 # for the thread
    start_new_thread( self.send, () )
  def __len__(self):
    return len(self.lines.keys())
  def free(self):
    self.stop()
    self.mix.pull_free()
    del self.mix
  def keys(self):
    return self.lines.keys()
  ################################################
  # thread

  def send(self):
    while 1:
      otask = self.otask # atomic op
      if otask:
        count = otask.pull()
        if count == 0:
          scount = self.sched()
          #print scount
          if scount == 0:
            print "Stream.send finish"
            self.otask = None # ?
            sleep(0.1)
            continue
      else:
        self.flag1 = 0 # OK i'm done
        sleep(0.1)

  def add(self,obuf):
    #print "Stream.add",obuf
    p = pipe( obuf, self.mix )
    self.lines[obuf] = p
  def rem(self,obuf):
    #print "Stream.rem",obuf
    try:
      p = self.lines[obuf]
      p.close()
      del self.lines[obuf]
    except KeyError:
      print " *** Stream.rem(%s) : Lost a buffer ",obuf
  def has(self,obuf):
    return self.lines.has_key( obuf )

  ################################################

  def started(self):
    return self.otask is not None
  def limit(self,i):
    #print "Stream.limit(%s)"%i
    assert i%2 == 0
    self.mixp.limit(i)
  def rlimit(self,i):
    self.mixp.rlimit(i)
  def no_limit(self):
    self.mixp.no_limit()
  def get_i(self):
    return self.mixp.get_i()
  def done(self):
    return self.mixp.done()
  def start(self, otask = None ):
    assert self.otask is None
    if otask is None:
      otask = DspWr(stereo=1)
    #self.obuf = Buffer(1024)
    self.obuf = Buffer(512)
    self.mixp = pipe( self.mix, self.obuf )
    self.limit(0)
    self.op = pipe( self.obuf, otask )
    self.otask = otask
  def stop(self):
    if self.op is None:
      assert self.otask is None
      assert self.flag1 == 0
      return
    #otask = self.otask
    if self.otask is not None:
      self.flag1 = 1
      self.otask = None
    while self.flag1:
      sleep(0.01) # hang around
    #if otask is not None:
      #self.rlimit(0)
      #while otask.pull():
        #pass
    self.op.close()
    self.op = None
    self.mixp.close()
    self.mixp = None
    self.obuf.free()
    self.obuf = None
    free_garbage()
  def reset(self):
    assert not self.lines
    count = self.il.pull_reset()
    #print "Stream.reset",count
  def pause(self):
    if self.op is None:
      assert self.otask is None
      assert self.flag1 == 0
      return
    if self.otask is not None:
      self.flag1 = 1
      self._otask = self.otask
      self.otask = None
    while self.flag1:
      pass # hang around
  def resume(self):
    assert self.otask is None
    if self._otask is not None:
      assert self.flag1 == 0
      self.otask = self._otask

#########################################################
#
#

class Stream2(Stream):
  " stereo Stream "
  def __init__(self, sched):
    self.otask = None
    self._otask = None
    self.op = None
    self.obuf = None

    self.il = Interleave()
    self.lbuf = Buffer()
    self.rbuf = Buffer()
    self.lp = pipe( self.lbuf, self.il )
    self.rp = pipe( self.rbuf, self.il )
    self.lmix = Add()
    self.rmix = Add()
    #Zero() | self.lmix
    #Zero() | self.rmix
    pipe(self.lmix,self.lbuf)
    pipe(self.rmix,self.rbuf)

    N = 4
    pans = [Pan2(self.lmix, self.rmix) for i in range(N)]
    for i in range(N):
      #r = float(i)*(N+1)/(N*N)
      r = float(i)/N+0.5/N
      #print r
      pans[i].set_pan(r)
    self.pans = [ pans[0], pans[-1], pans[1], pans[-2] ]
    
    self.mixs = [ Add() for  i in range(N)]
    for i in range(N):
      pipe( self.mixs[i], self.pans[i].ibuf )
      Zero() | self.mixs[i]

    self.sched = sched
    self.lines = {}
    self.flag1 = 0 # for the thread
    start_new_thread( self.send, () )
  def add(self,obuf,i=0):
    #print "Stream.add",obuf
    #p = pipe( obuf, self.lmix )
    p = pipe( obuf, self.mixs[i%len(self.mixs)] )
    self.lines[obuf] = p
  def free(self):
    self.stop()
    self.il.pull_free()

  ################################################

  def started(self):
    return self.otask is not None
  def limit(self,i):
    if i%2:
      print "Stream2.limit(%s)"%i
    assert i%2 == 0
    #print "Stream2.limit() rlimit = ",i-self.get_i()
    self.mixp.limit(i*2) # stereo
  def rlimit(self,i):
    assert i%2 == 0
    print "Stream2.rlimit ",i
    if i!=65536:
      assert 0 # backtrace
    self.mixp.rlimit(i*2) # stereo
  def no_limit(self):
    self.mixp.no_limit()
  def get_i(self):
    i = self.mixp.get_i()
    i = int(i//4)*4
    return i//2 # stereo
  def done(self):
    return self.mixp.done()

  def start(self, otask = None ):
    assert self.otask is None
    if otask is None:
      otask = DspWr(stereo=1)
    #self.obuf = Buffer(1024)
    #self.obuf = Buffer(512)
    self.obuf = Buffer()
    self.mixp = pipe( self.il, self.obuf )
    self.limit(0)
    self.op = pipe( self.obuf, otask )
    self.otask = otask


