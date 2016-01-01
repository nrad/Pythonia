#!/usr/bin/env python

from Sonic import *
from random import random, choice, randrange
from math import sin

#
# Quad channels
#
class Quad:
  def __init__(self,otask0,otask1):
    il0 = Interleave()
    il1 = Interleave()
    il0 | otask0
    il1 | otask1
    ils = [il0,il1]
    mixs = []
    for il in ils:
      for i in range(2):
        mix = Add()
        mix | il
        mixs.append( mix )
        Zero() | mix
        #Sin( random()*880 ) | mix
    self.otask0=otask0
    self.otask1=otask1
    self.mixs=mixs
    self.mix00,self.mix01,self.mix10,self.mix11 = mixs
  def pull(self):
    return self.otask0.pull() + self.otask1.pull()
  
#
# Pan
#
class Pan:
  " export ibuf "
  def __init__(self, *otasks):
    chains = []
    ibuf = Buffer()
    for otask in otasks:
      gain = Gain(0.1)
      p0,p1,p2 = pipe(ibuf, gain, Buffer(), otask)
      chains.append( (p0, gain, p1, p2) )
    self.chains=chains
    self.ibuf=ibuf
  def set_r(self,i,r):
    self.chains[i][1].set_r( r )
  def set_v(self,v):
    for i in range(len(v)):
      self.set_r(i,v[i])
  def __del__(self):
    for p0, gain, p1, p2 in self.chains:
      p0.close()
      p1.close()
      p2.close()

class Pan2(Pan):
  " two channels "
  def __init__(self, *otasks):
    assert len(otasks)==2
    Pan.__init__(self,*otasks)
    self.set_pan(0.5)
  def set_pan(self,r):
    #assert 0<=r<=1.0
    self.set_r(0,r)
    self.set_r(1,1.0-r)

class Stereo:
  " export lbuf rbuf "
  def __init__(self,otask):
    otask = otask
    il = Interleave()
    self.lbuf = Buffer()
    self.rbuf = Buffer()
    pipe( self.lbuf, il )
    self.op = pipe(
      self.rbuf, il, Buffer(), otask )[-1]

class Select:
  def __init__(self,mixs):
    self.mixs=mixs
    self.tasks=[]
  def remove(self,i):
    task, p0, p1, p2, p3 = self.tasks[i]
    self.tasks.pop(i)
    task.push()
    p0.close()
    p1.close()
    p2.close()
    p3.close()
  def send(self):
    #print [ play.done() for play in plays ]
    i=0
    while i < len(self.tasks):
      task, p0, p1, p2, p3 = self.tasks[i]
      if task.done():
        self.remove(i)
        gc.collect()
      else:
        i = i+1
  def add(self,task,r=0.4):
    mix = choice(self.mixs)
    #task | mix
    #b = Buffer()
    p0, p1, p2, p3 = pipe( task, Buffer(), Gain(r), Buffer(), mix )
    self.tasks.append((task, p0, p1, p2, p3))

class Sweep:
  " dual of Select "
  def __init__(self,mix):
    self.mix = mix # otask
    self.lines = []
  def add(self,itask,r=0.6):
    zero=Zero() # off
    buf = Buffer()
    osw = OSwitch([zero,itask],buf)
    gain = Gain(r)
    ps = pipe( buf, gain, Buffer(), self.mix )
    self.lines.append( (itask,osw,gain,ps) )
  def set_on(self,i,on):
    assert on==1 or on==0
    itask, osw, gain, ps = self.lines[i]
    osw.to(on)
  def set_r(self,i,r):
    assert on==1 or on==0
    itask, osw, gain, ps = self.lines[i]
    gain.set_r(r)
  def remove(self,i):
    itask, osw, gain, ps = self.lines.pop(i)
    itask.push()
    for p in ps:
      p.close()


