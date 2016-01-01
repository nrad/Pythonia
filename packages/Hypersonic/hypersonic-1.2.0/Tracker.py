#!/usr/bin/env python

from __future__ import nested_scopes

import sys
from time import *
#from Sonic import *
from Stream import *

try:
  import psyco
  psyco.full()
except:
  pass

null_log()

class ELoop:
  def __init__(self, filename, quant=128):
    self.filename=filename
    self.mm=MMap(self.filename)
    #self.gain = None
    #self.rmod = None
    #self.loop = None
    #self.env = None
    self.obuf = None

    self.gain = Gain(0.0)
    self.rmod = RMod()
    sz = int(os.stat(filename)[6])
    sz = int( sz // quant ) * quant
    self.loop = Loop(self.mm, sz)
    self.frames = self.loop.sz/2
    w = 128
    self.env = Linear(((w,1<<14), (self.frames-w*2,1<<14), (w,0)))
    self.lbuf = Buffer()
    self.rbuf = Buffer()
    self.ps = pipe(
      self.loop, self.lbuf,
      self.rmod, self.rbuf,
      self.gain )
    self.lp = self.ps[0]
    self.ebuf = Buffer()
    self.ps += pipe( self.env, self.ebuf, self.rmod )

  def __str__(self):
    return "ELoop(%s,%f)"%(self.filename,self.gain.get_r())
  def rlimit(self,i=1):
    #self.op.rlimit( 2*self.frames )
    self.lp.rlimit( 2*self.frames*i )
    assert self.loop.get_offset() == 0
  def set_r(self,r):
    #print self,"set_r",r
    self.gain.set_r(r)
  def get_i(self):
    return self.lp.get_i()
  def done(self):
    return self.lp.done()
  def open(self,obuf,r = 0.0):
    assert self.obuf is None
    self.gain.set_r(r)
    self.obuf = obuf
    self.op = pipe( self.gain, obuf )
  def close(self):
    self.op.close()
    self.op = None
    self.obuf = None
    self.gain.pull_reset()
    #self.lbuf.reset()
    #self.rbuf.reset()
    #self.ebuf.reset()
    self.loop.seek(0)
    #self.env.reset()
  def free(self):
    if self.obuf is not None:
      self.close()
    count = self.gain.pull_free()
    self.mm.free()
    del self.mm
    #print "eloop free:",count

#
##################################################
#

class Track:
  def __init__(
      self,filename,
      span=4096*512,n=None,data=None,tracki=0,**kw):
    self.filename = filename
    self.eloop = ELoop(self.filename)
    self.obuf = None
    #self.frames = int(os.stat(filename)[6]//2) # frames
    self.frames = self.eloop.frames
    #print self.frames
    self.r = 0.8
    self.tracki = tracki
    ######

    self.span=span
    self.data={}
    n = span / self.frames
    if data is not None:
      if type(data)==list:
        for i in range(len(data)):
          if data[i]:
            self.data[i] = data[i]
            n = i+1
      else:
        for i in data:
          if data[i]:
            self.data[i] = data[i]
            n = max(n,i+1)
    self.n = int(n)
    for key in kw.keys():
      self.__dict__[key] = kw[key]

  def __len__(self):
    #return len(self.data)
    return self.n
  def __setitem__(self,idx,val):
    #print "Track.__setitem__(%s,%s,%s)"%(self,idx,val)
    #print "Track.__setitem__(%s,%s)"%(idx,val)
    assert type(idx) == int
    self.data[idx]=val
    if val == 0.0:
      del self.data[idx]
  def __getitem__(self,idx):
    assert type(idx) == int or type(idx) == long
    #if idx >= self.n or 0 > idx:
      #raise IndexError
    if self.data.has_key(idx):
      return self.data[idx]
    return 0.0
  def keys(self):
    return self.data.keys()
  def bump(self,i=1):
    data = {}
    for key in self.data.keys():
      if key+i>=0:
        data[key+i]=self.data[key]
    self.data=data
  def __repr__(self):
    return "Track('%s',%s,data=%s,tracki=%d)"%\
      (self.filename,self.span,self.data,self.tracki)
    #return "Track(%s,frames=%s,done=%s)"%\
      #(self.eloop,self.eloop.frames,self.done())
  def __str__(self):
    return "Track(%s,frames=%s,done=%s)"%\
      (self.eloop,self.eloop.frames,self.done())
  def items(self):
    return self.data.items()
  def _get_events(self,frame=0):
    # need every on event, only one off event
    events = []
    frame = int(frame) 
    #assert type(frame)==int or type(frame)==long
    idx0 = frame // self.frames
    if idx0 % self.frames:
      idx0 += 1
    idx = idx0
    while idx < len(self):
      if self[idx] > 0.0:
        events.append( idx*self.frames*2 ) # bytecount
      elif self[idx] == 0.0 and \
          (idx > idx0 and self[idx-1] > 0):
        assert events and events[-1] == (idx-1)*self.frames*2
        events.append( idx*self.frames*2 ) # bytecount
      idx += 1
    #print "get_events",i,events
    return events
  def get_events(self,frame=0):
    # need every on event, only one off event
    events = []
    frame = int(frame) 
    #assert type(frame)==int or type(frame)==long
    idx0 = frame // self.frames
    if idx0 % self.frames:
      idx0 += 1
    idx = idx0
    #while idx < len(self):
    for key,val in self.data.items():
      if key<idx:
        continue
      assert val>0.0
      events.append( key*self.frames*2 ) # bytecount
      if key+1==self.n or (key+1<self.n and self[key+1]==0.0):
        events.append( (key+1)*self.frames*2 ) # bytecount
    #print "get_events",i,events
    events.sort()
    #_events = self._get_events(frame)
    #if events != _events:
      #print len(events),len(_events)
      #print events
      #print _events
      ##assert 0
    return events
  def set_r(self,r):
    #print self,"set_r",r
    self.eloop.set_r(r)
  def done(self):
    return self.eloop.done()
  def open(self,i=0):
    assert self.obuf is None
    self.obuf = Buffer()
    self.eloop.open( self.obuf )
    self.eloop.rlimit(i)
  def close(self):
    self.eloop.close()
    self.obuf.free()
    self.obuf = None
  def free(self):
    self.eloop.free()
    if self.obuf is not None:
      self.obuf.free()
    self.obuf = None
  def is_open(self):
    return self.obuf is not None
  def get_i(self):
    return self.eloop.get_i()

  # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # thread 

  def block_seek(self,i,stream):
    idx = i // (self.frames*2)
    if i % (self.frames*2):
      print "***",self.eloop.done(),\
        self.get_i(),\
        Self.get_i()%(self.frames*2)
      assert 0
      return
    skip = self.get_i() % (self.frames*2)
    if skip:
      print "*** skip",self.filename,skip
      assert 0
    val = self[idx]
    #if idx < len(self):
      #val = self[idx]
    #else:
      #val = 0.0

    #print "block_seek",self.filename,i,self.eloop.get_i()
    self.eloop.set_r(val*self.r)
    self.eloop.rlimit(1)
    #if val > 0.0 and (idx == 0 or self[idx-1] == 0):
      #stream.add( self.obuf )
    #elif val == 0.0 and (idx > 0 and self[idx-1] > 0):
      #stream.rem( self.obuf )
    if val > 0.0 and not stream.has( self.obuf ):
      stream.add( self.obuf, self.tracki )
    elif val == 0.0 and (idx > 0 and self[idx-1] > 0):
      stream.rem( self.obuf )

  # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def reset(self):
    self.eloop.reset()

#
##################################################
#

class Queue(list):
  def __init__(self,items=[]):
    self[:] = items
  def add(self,target,events):
    num = len(self)
    # assert ##############
    _event = -1
    for event in events:
      assert _event <= event
      _event = event
    #######################
    i=0
    j=0
    while i < len(events) and j < len(self):
      event = events[i]
      _target, _event = self[j]
      if event < _event:
        self.insert( j, (target,event) )
        i+=1
      j+=1
    while i < len(events):
      self.append( (target,events[i]) )
      i+=1
    #if i < len(events):
      #self += [ (target,event) for event in events[i:] ]
    # assert ##############
    _event = -1
    for target, event in self:
      assert _event <= event
      _event = event
    #######################
    assert len(self) == num + len(events)
  def flush(self):
    self[:] = []
  def get_next(self):
    if self:
      return self[0]
  def pop_next(self):
    if self:
      return self.pop(0)
    
#
##################################################
#

class Tracker:
  def __init__(self,tracks=None):
    if tracks:
      self.tracks=tracks
    else:
      self.tracks=[]
    self.stream = Stream2(self.sched)
    self.queue = Queue()
    self.offset = None
    self.cache = {}
  def __repr__(self):
    s = map( repr, self.tracks )
    s = string.join( s, ",\n" )
    return "Tracker([%s])"%s
  def __len__(self):
    return len(self.tracks)
  def __getitem__(self,idx):
    return self.tracks[idx]
  def free(self):
    self.stream.free()
    for track in self.tracks:
      track.free()
  def append(self,item):
    self.tracks.append(item)

  # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # thread 

  def sched(self):
    #print "sched"
    count = 0
    i = self.stream.get_i() + 2*self.offset
    key = i,self.stream.get_i(),2*self.offset
    if self.cache.has_key(key):
      self.cache[key]+=1
      if self.cache[key]>10:
        # been here 10 times
        #for x in self.stream.otask.pull_find():
          #print x
        #print self.stream.otask.pull_str()
        print "been here 10 times"
        return 0
    else:
      self.cache = { key : 1 }
    #print "sched",key
    next = self.queue.get_next()
    if next is None:
      print "Tracker.sched: next is None"
    while next is not None:
      track, _i = next
      assert _i >= i
      if _i > i:
        assert _i > i
        self.stream.limit( _i - 2*self.offset )
        #print "(",_i-i,")"
        return count+1 # keep going
      track.block_seek( _i, self.stream )
      self.queue.pop_next()
      count += 1
      next = self.queue.get_next()
    print "Tracker.sched: no_limit", count
    if count:
      # call me again
      self.stream.rlimit( 4096*16 )
    else:
      self.stream.no_limit()
    return count

  # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def started(self):
    #return self.stream.started()
    #return len(self.queue) != 0
    return self.tracks and self.tracks[0].is_open()
  def play1(self, tracki):
    print "Tracker.play1"
    if self.started():
      self.stop()
    track = self[tracki]
    assert not track.is_open()
    track.open(1)
    track.set_r(0.4)
    #otask = DspWr(stereo=1)
    otask = DspWr()
    op = pipe( track.obuf, otask )
    op.rlimit( track.frames*2 ) # bytecount
    while not op.done():
      print otask.pull()
    op.close()
    track.close()
    otask.free()
    
  def start(self, otask=None, offset=0):
    print "Tracker.start",offset
    if self.started():
      self.stop()
    assert len(self.queue) == 0
    self.offset = 2*(int(offset)//2)
    for track in self:
      #print "Tracker.start: get_events"
      events = track.get_events(offset) 
      #print "Tracker.start: add", len(events)
      self.queue.add( track, events )
      #print "Tracker.start: open"
      track.open()
      #track.block_seek( 0 )
      #self.stream.add( track.obuf )
    for track,i in self.queue:
      #assert i >= 2*offset
      if i%2:
        print " *** Tracker.start: alignment error "
        self.stream.start( otask )
        self.stop()
        raise Exception, track
    self.stream.start( otask )
  def reset(self):
    self.stop()
    self.start()
  #def seek(self, i):
    #self.stream.pause()
    #for track in self:
      #track.seek(i)
    #self.stream.resume()
  def stop(self):
    print "Tracker.stop"
    if self.started():
      self.stream.stop()
      for obuf in self.stream.keys():
        self.stream.rem( obuf )
      self.stream.reset()
      print "Tracker.stop close"
      for track in self.tracks:
        track.close()
    self.queue.flush()
    self.offset = None
    free_garbage()
    print "Tracker.stop done"
  def rec(self,fnam="ofile.raw"):
    print "Tracker.rec",fnam
    #return
    fwr=FileWr(fnam)
    self.start(fwr)

