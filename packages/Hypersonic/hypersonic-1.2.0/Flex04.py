#!/usr/bin/env pythonw

from __future__ import nested_scopes
from __future__ import generators
#from TSerial import *
from random import *
from math import pi, sin, sqrt
import math

from time import sleep

#from Kr import *
##from PlayBuf import *
##from Sched import *
##from Tree import *
##from sampfs import *

#############################

if 0:
  #from Kr import *
  from SuperCollider import *
  from TSerial import *
  from random import choice, random, randint
  #from KrUI import *
  #from TSerial import *

#############################

from Sonic import *

#SMIN = -0x7FFF
#SMAX = 0x7FFF

null_log()

def mkv():
  return (randint(32,256), choice([SMIN,SMAX]) )
  return (randint(32,256), randint(SMIN,SMAX) )

def mkpart(n,m):
  # return partition of n into at most m pieces
  p=[ randrange(1,n) for i in range(m-1) ]
  p.sort()
  _p=[]
  op=0
  for i in range(len(p)):
    if p[i]>op:
      _p.append(p[i]-op)
    op=p[i]
  if op<n:
    _p.append(n-op)
  #print reduce(lambda x,y:x+y,_p)
  return _p

def mkv(n,m):
  part = mkpart(n,m)
  v = [ ( x, choice((SMIN,SMAX)) ) for x in part ]
  v[-1] = ( v[-1][0], 0 )
  return v

def test00():
  lin = Linear( mkv(256,5) )
  dsp = DspWr()
  t = Sin(1.0)
  b = Buffer(1<<17)
  b.fill( t )
  lookup = Lookup( b ) 
  lin | lookup | dsp
  while 1:
    dsp.pull()
    #lin[ randint( 0,4 ) ] = mkv()
    #lin[ 0 ] = mkv()

#
######################################################
#

class ADSR(Linear):
  def __init__(self,W,A,D,S,R):
    Linear.__init__( self, [(A,SMAX), (D,S), (W-A-D-R,S), (R,0)] )
    self.W=W
    self.A=A
    self.D=D
    self.S=S
    self.R=R
  def update(self,W=None,A=None,D=None,S=None,R=None):
    #!! overrides !!
    if W is not None:
      self.W=W
    if A is not None:
      self.A=A
    if D is not None:
      self.D=D
    if S is not None:
      self.S=S
    if R is not None:
      self.R=R
    if self.W <= self.A+self.D+self.R:
      #raise Exception, ( self.W, self.A, self.D, self.S, self.R )
      return
    v = [(self.A,SMAX), (self.D,self.S),
     (self.W-self.A-self.D-self.R,self.S), (self.R,0)]
    for idx in range(len(v)):
      self[idx] = v[idx]

class PWConst(Linear):
  " piecewise constant (almost) "
  def __init__(self, W, w, levs):
    assert W>w
    v = []
    for lev in levs:
      v.append( (w,lev) )
      v.append( (W-w,lev) )
    _v = [ (_w, lev) for lev in levs for _w in (w,W-w) ]
    assert _v == v
    Linear.__init__(self, v)
    self.w = w
    self.W = W
  def __setitem__(self, idx, lev):
    #print "PWConst.__setitem__",idx,lev, self.W, self.w
    Linear.__setitem__(self, idx*2, (self.w,lev) )
    Linear.__setitem__(self, idx*2+1, (self.W-self.w,lev) )

from operator import sub, mul
def gcd(a,b):
  """Kirby's Extended Euclidean Algorithm for GCD"""
  v1 = [a,1,0]
  v2 = [b,0,1]
  while v2[0]<>0:
    p = v1[0]//v2[0]
    v2, v1 = map(sub,v1,[p*vi for vi in v2]), v2
  return v1

class GCDEnv(PWConst):
  def __init__(self, W, w, N, rN = None, thr = 0.0, exp = 1.0 ):
    assert type(N)==int
    if rN is None:
      rN = N
    assert type(rN)==int
    #print [ ('gcd',N,i,'=',gcd( N, i )) for i in range(N) ]
    levels = [ (( gcd( rN, i )[0] / float(rN) )**exp ) for i in range(N) ]
    for i in range(len(levels)):
      if levels[i] < thr:
        levels[i] = 0.0
    levels = [ level * SMAX for level in levels ]
    #print levels
    PWConst.__init__( self, W, w, levels )
    self.N = N
    self.rN = rN
    self.thr = thr
    self.exp = exp
  def update(self, rN=None, thr=None, exp = None ):
    #!! overrides !!
    "rN: relative N"
    if rN is not None:
      self.rN = rN
    if thr is not None:
      self.thr = thr
    if exp is not None:
      self.exp = exp
    for i in range(self.N):
      level = (( gcd( self.rN, i )[0] / float(self.rN) )**self.exp )
      if level < self.thr:
        level = 0
      self[i] = SMAX * level

#
######################################################
#

def Src00(N=32, W=None, kline = [ 3.0 / 2, 1.0, 5/4.0, 4.0/5 ] ):
  #seed(1)
  st = 2 ** (1/12.0)
  #eflat = 440 * (2**0.5)
  eflat = 220 * (2**0.5)
  #freqs = [ eflat * ( st ** i ) for i in range(12) ]
  kappa = 1.0
  freqs = []
  for i in range(N):
    freqs.append( eflat * kappa )
    kappa *= choice( kline )
    #if random() < 0.4:
      #kappa = choice( kline )
    while kappa > 2.0:
      kappa /= 2.0
    while kappa < 1.0/2:
      kappa *= 2.0
  taps = [ int(44100 / freq) for freq in freqs ]
  #print freqs
  return [ Linear( mkv(tap,5) ) for tap in taps ]

def Src01(W):
  global loops
  #src = [ Loop( "/raw/done/%s"%name ) for name in os.listdir( "/raw/done" )[:N] ]
  #src = [ Loop( "/raw/done/%s"%choice(os.listdir( "/raw/done" )))
    #for i in range(N) ]
  #src = [ Loop( "/raw/done/%s"%name ) for name in os.listdir( "/raw/done" ) ]
  ms = [ MMap( "/raw/done/%s"%name ) for name in os.listdir( "/raw/done" ) ]
  print "sz = ",W*4
  src = [ Loop(m, W*4) for m in ms ]
  loops = src
  #src = [ choice( src ) for i in range(N) ]
  _src = []
  for t in src:
    split = Split()
    t | split
    mix = Mix(0.5)
    #copy = Copy()
    #split | copy | mix
    #copy = Copy()
    #split | copy | mix
    split | mix
    split | mix
    _src.append( mix )
  return _src

def Src02(N=None,W=None):
  global loops
  #src = [ Loop( "/raw/done/%s"%name ) for name in os.listdir( "/raw/done" )[:N] ]
  #src = [ Loop( "/raw/done/%s"%choice(os.listdir( "/raw/done" )))
    #for i in range(N) ]
  #src = [ Loop( "/raw/done/%s"%name ) for name in os.listdir( "/raw/done" ) ]
  names = [name for name in os.listdir( "/raw/done" ) if name.endswith(".raw") ]
  if N is not None:
    name = name[:N]
  ms = [ MMap( "/raw/done/%s"%name ) for name in names ]
  #print "sz = ",W*2
  #src = [ Loop(m, W*2) for m in ms ]
  src = [ Loop(m) for m in ms ]
  loops = src
  return src

class Phonic:
  def __init__(self, W, src):
    self.W = W
    self.Ns = 2,2,3,5

    self.zero = Zero()
    
    self.src = src
  
    A, D, S, R = 256, 256, SMAX/32, 64
    self.env1 = ADSR( W, A, D, S, R )
    rmod1 = RMod()
    self.env1 | rmod1
  
    w = 128
    self.env2 = GCDEnv( W, w, 16, thr = 0.0 )
    rmod2 = RMod()
    self.env2 | rmod2
  
    self.ibuf = Buffer()
    r = 1.0
    self.resample = Resample( r )
    self.obuf = Buffer(W*8)
    ps = pipe( 
      self.ibuf, self.resample,
      #ibuf, rmod1,
      Buffer(), rmod1,
      #ibuf, rmod1,
      Buffer(), rmod2,
      #Buffer(), resample,
      self.obuf )
    self.op = ps[-1]
    self.limp = ps[2] # <---------- watch it !
  def set(self,idx):
    if idx is None:
      t = self.zero
    else:
      t = self.src[idx]
    self.ip = pipe( t, self.ibuf )
    self.limp.rlimit( self.W*2 )
    #print "resample",resample.get_r()
    #print "rlimit",W*2
  def set_src(self,src):
    self.src = src
  def done(self):
    return self.limp.done()
  def reset(self):
    assert self.limp.get_rlimit() == 0
    #ip.rlimit( W*2 )
    #print "*",
    self.limp.pull_reset()
    #self.obuf.pull_reset()
    #self.rmod1.pull_reset()
    self.ip.close()
  def mod(self):
    if random() < 0.1:
      A = randint( 16, self.W/16 ) * 8
      print "A", A
      self.env1.update( A=A )
    if random() < 0.1:
      D = randint( 16, self.W/4 ) * 2
      print "D", D
      self.env1.update( D=D )
    if random() < 0.1:
      S = SMAX / randint( 1, 8 )
      print "S", S
      self.env1.update( S=S )
    #if random() < 0.1:
      #R = randint( 32, 512 ) * 2
      #print "R", R
      #self.env1.update( R=R )
    if random() < 0.01 and 0:
      #r = choice( [ 2**( -i ) for i in range(4) ] )
      r = choice( [ 3/4.0, 4.0/3, 5.0/4, 4.0/5, 1.0, 0.5 ] )
      #r = choice( kline )
      self.resample.set_r(r)
      print "r",r
    if random() < 0.05:
      #rN = randint(1,N)
      rN = choice( self.Ns )
      self.env2.update( rN=rN )
      print "rN",rN
    #if random() < 0.1:
      #level = random()**2
      #env2.update( thr = level )
      #print "level",level
    if random() < 0.01:
      exp = random()*2
      self.env2.update( exp = exp )
      print "exp",exp

#
######################################################
#

class Idx00:
  def __init__(self,N):
    self.N = N
    self.idx = 0
  def __iter__(self):
    while 1:
      yield self.idx
      self.idx += 1
      self.idx %= self.N
  def mod(self):
    if random() < 0.1:
      self.idx = randint( 0, self.N - 1 )

class Idx01:
  def __init__(self,N,Ns=(2,2,3,5,7)):
    self.N = N
    self.Ns = Ns
    self.idx = 0
    self.didx = 1
  def __iter__(self):
    while 1:
      yield self.idx
      self.idx += self.didx
      self.idx %= self.N
  def mod(self):
    if random() < 0.02:
      self.idx = randint( 0, self.N - 1 )
      print "idx",self.didx
    if random() < 0.02:
      self.didx *= choice( self.Ns )
      print "didx",self.didx
    if random() < 0.03:
      self.didx = randint( 1, self.N-1 )
      print "didx",self.didx

class Idx02:
  def __init__(self,N,Ns=(2,2,3,5,7)):
    self.N = N
    self.didx = 1
    self.idxi = 0
    #self.idxs = [None]*N
    #self.idxs[0] = 0
    self.idxs = [0]*N
    #self.idxs = [ i for i in range(N) ]
  def __iter__(self):
    while 1:
      self.idxi += self.didx
      self.idxi %= self.N
      yield self.idxs[self.idxi]
  def mod(self):
    if random() < 0.4:
      #idx = choice( range(N) )
      idx = choice( self.idxs )
      if idx is None:
        idx = 0
      else:
        idx += 1
        idx %= self.N
      print "idx",idx
      #idxs[ choice(range(N)) ] = idx
      self.idxs[ self.idxi ] = idx
    if random() < 0.1:
      print "del"
      self.idxs[ self.idxi ] = None

class Idx020(Idx02):
  def __init__(self,N,Ns=(2,2,3,5,7)):
    self.N = N
    self.didx = 1
    self.idxi = 0
    self.idxs = [None]*N
    #self.idxs[0] = 0
    #self.idxs = [0]*N
    #self.idxs = [ i for i in range(N) ]

#
######################################################
#

class Echo00:
  def __init__(self,W,N,DELAY,ibuf,otask,taps=None):
    self.DELAY = DELAY
    self.W = W
    self.N = N
    if taps == None:
      #taps = [ (-256*i,1.0/N) for i in range(N) ]
      taps = [ (-512*i,1.0/N) for i in range(N) ]
    self.iir = IIR()
    for i,r in taps:
      self.iir.add( i, r )
    pipe( ibuf, self.iir, Buffer(W*8), Mix(0.4), Buffer(), otask )
  def mod(self):
    if random() < 0.05:
      DELAY = randint( 2, self.DELAY )
      self.iir[randint(1,self.N-1)].set_i( -256*DELAY )
      print "iir",DELAY

class Echo01:
  def __init__(self,W,N,nbuf,il):
    rN = N/3
    exp = 1.0
    levels = [ (( gcd( rN, i )[0] / float(rN) )**exp ) for i in range(N) ]

######################################################
#
######################################################

def test01():
  W = 4096 + 512 + 512
  #W *= 2
  #W = 4096 - 512 - 512
  #W = 2048

  #N = 16 * 4
  Ns = 2,2,3,5
  N = reduce( mul, Ns )
  #src = Src02(W=W, N=N)

  #dsp = DspWr(stereo=1,fpb=512)
  dsp = DspWr(stereo=1)
  #dsp = FileWr("out.02.raw")
  il = Interleave()
  il | dsp

  srcs = []
  mixs = [Mix(0.5), Mix(0.5)] # chan 0, 1
  phonics = []
  echos = []
  idxers = []
  gens = []

  # chan 0
  mixs[0] | il
  #srcs.append( Src02(W=W,N=N) )
  srcs.append( Src00(W=W,N=N) )
  phonics.append( Phonic( W, srcs[-1] ) )
  #echos.append( Echo00( W+512, 4, 12*4, phonics[-1].obuf, mixs[1] ) )
  #pipe( phonics[-1].obuf, mixs[0] )
  #pipe( phonics[-1].obuf, mixs[0] )
  join( phonics[-1].obuf, Gain(0.8), mixs[0] )
  #join( phonics[-1].obuf, Gain(0.03), mixs[0] )
  idxers.append( Idx01(N) )
  gens.append( iter(idxers[-1]) )
  phonics[-1].set( gens[-1].next() )

  # chan 1
  #W = (W+128)*2
  #W = W+128
  mixs[1] | il
  srcs.append( Src00(W=W,N=N) )
  #srcs.append( Src01(W=W) )
  phonics.append( Phonic( W*4, srcs[-1] ) )
  #echos.append( Echo00( W*2, 4, 12*6*4, phonics[-1].obuf, mixs[0] ) )
  #pipe( phonics[-1].obuf, mixs[1] )
  #join( phonics[-1].obuf, Gain(0.4), mixs[1] )
  join( phonics[-1].obuf, Gain(0.8), mixs[1] )
  idxers.append( Idx01(N) )
  gens.append( iter(idxers[-1]) )
  phonics[-1].set( gens[-1].next() )

  ##########################
  count = 0
  done = 0
  while count < 1024 or 1:
    if done:
      break
    for i in range(1):
      #while not phonic1.done() and not phonic2.done():
      try:
        while dsp.pull():
          pass
      except KeyboardInterrupt:
        done = 1
        #raise KeyboardInterrupt
        #break
      #while dsp.pull():
        #pass
      #if idx is not None:
        #print "offset",loops[idx].get_offset()
      for chan in range(2):
        if phonics[chan].done():
          phonics[chan].reset()
          phonics[chan].set( gens[chan].next() )
          #if random() < 0.2:
            #continue
          phonics[chan].mod()
      if 1:
        for idxer in idxers:
          idxer.mod()
        for echo in echos:
          echo.mod()
          #if count % 1024 == 0:
            #print "\t"*4,"src"
            #phonic1.set_src( src = Src00(N=N) )
    count += 1

#seed(3)
#import gc
if __name__=="__main__":
  if sys.argv[1:]:
    es = "test%s()"%sys.argv[1]
    try:
      exec es
    except KeyboardInterrupt:
      pass
    print "all over"
    #sleep(0.1)
    #print gc.collect()
    #sleep(0.1)
    try:
      usb.record()
    except NameError, e:
      pass
    #import profile
    #profile.run( es, 'profile.out' )
    #stats = profile.Stats( 'profile.out' )
    #stats.print_stats()
  else:
    test01()



