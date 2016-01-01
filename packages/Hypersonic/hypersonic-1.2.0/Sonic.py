#!/usr/bin/env python

from __future__ import nested_scopes
from __future__ import generators
from time import time, sleep
#from types import *
import sys, os
import string
import sonic
import gc
from cmdopts import *

try:
  import NoModule
  import psyco
  psyco.full()
  from psyco.classes import *
except ImportError:
  #class _psyco:
    #def jit(self):      pass
    #def bind(self, f):  pass
    #def proxy(self, f): return f
  #psyco = _psyco()
  pass

try:
  import OSS_defs
except ImportError:
  print "OSS_defs.py not found"

#arch = None
#if __name__=="__main__":
  #if sys.argv[1:]:
    #arg = sys.argv[1]
    #if arg.count("="):
      #exec arg

def set_log(file):
  global logfile
  logfile=file
def null_log():
  set_log( open("/dev/null","w") )
def log(*s):
  file=logfile
  for _s in s:
    file.write( str(_s)+" " )
  file.write("\n")
  file.flush()
set_log(sys.stdout)
#null_log()

bufsz=4096 # default buffer size
dsp=0,44100,0 # device, speed, stereo
soundcard="OSS"
fpb=1024 # used by portaudio
#soundcard="portaudio"
hypersonicrc=os.environ["HOME"]+"/.hypersonicrc"
#print "reading %s"%hypersonicrc
try:
  rcfile = open(hypersonicrc)
  s = rcfile.read()
  #print "exec %s"%s
  exec( s, locals(), globals() )
except IOError:
  print "could not find %s, creating default"%hypersonicrc
  rcfile = open( hypersonicrc, "w" )
  rcfile.write( "bufsz = %s # default buffer size\ndsp=%s # device, speed, stereo\n"%(bufsz,dsp) )
  #rcfile.write( "arch=%s\n"%repr(arch) )
  rcfile.write( "soundcard=%s\n"%repr(soundcard) )

SMAX = 0x7FFF
SMIN = -0x7FFF

def xmark():
  sonic.xmark()
def xcheck():
  free_garbage()
  x=sonic.xcheck()
  if(x):
    log("  ********  Memory leak :",x,"************")
  return x

def file_exists(fnam):
  try:
    os.stat(fnam)
    return 1
  except OSError:
    return 0

class Buffer:
  " Buffer(size): just some memory "
  #buffers={}
  def __init__(self,size=bufsz):
    self.size=size
    self.b=sonic.buffer_new(size)
    #Buffer.buffers[self]=self
    self.id=sonic.buffer_id(self.b)
    self.pipes=[]
    log("Buffer.__init__(%d)=%s"%(size,str(self)))
  def __call__(self, *args):
    #tree = []
    for x in args:
      if isinstance( x, Task ):
        x.open_writer( self )
      elif isinstance( x, Buffer ):
        pipe( x, Copy(), self )
        print "Note: buffer to buffer via copy"
      else:
        raise TypeError, "Don't know how to connect to", x
    return self # ??? how to make this compatible with | ???
  def send(self):
    assert self.b
    return sonic.buffer_send(self.b)
  def pull(self):
    count=0
    for p in self.pipes:
      if p.is_writer:
        count+=p.pull()
    return count+self.send()
  def push(self):
    count=self.send()
    for p in self.pipes:
      #print "Buffer.push"
      if p.is_reader:
        count+=p.push()
    return count
  def sources(self):
    return map(lambda p:p.source(),
      filter(lambda p:p.is_writer,self.pipes))
  def targets(self):
    return map(lambda p:p.target(),
      filter(lambda p:p.is_reader,self.pipes))
  def fill(self,task):
    p0, p1 = pipe( task, self, Null() )
    count = 1
    while count:
      count=self.pull() + self.pull()
    p0.close()
    p1.close()
  def __str__(self):
    #if not self.b: return "b?"
    #return "b%d"%sonic.buffer_id(self.b)
    return "b%d"%self.id
  def __repr__(self):
    return "Buffer(%s)"%self.size
  def pipe(self,task):
    return task.open_reader(self) # confused yet?
  def append(self,p):
    self.pipes.append(p)
  def remove(self,p):
    self.pipes.remove(p)
  def reset(self):
    sonic.buffer_reset(self.b)
    for p in self.pipes:
      p.reset()
  def free(self):
    log("buffer_free(%s)"%self)
    while self.pipes: self.pipes[-1].close()
    assert self.b
    sonic.buffer_free(self.b)
    self.b=None
  def pull_free(self):
    count=0
    for p in self.pipes[:]:
      if p.is_writer:
        count+=p.pull_free()
    self.free()
    return count+1
  def pull_reset(self):
    count=0
    for p in self.pipes[:]:
      if p.is_writer:
        count+=p.pull_reset()
    self.reset()
    return count+1
  def pull_visit(self):
    for p in self.pipes[:]:
      if p.is_writer:
        for x in p.pull_visit():
          yield x
    yield self
  def pull_str(self,depth):
    #s = [ "  "*depth+"%s\n"%repr(self) ]
    #s = [ " %s"%repr(self) ]
    s = [ " |" ]
    for p in self.pipes[:]:
      if p.is_writer:
        s.append( p.pull_str(depth) )
    return "".join(s)
  def __del__(self):
    log("Buffer.__del__(%s)"%str(self))
    if self.b:
      self.free()
del bufsz

class Pipe:
  " Pipe(x,y): connects a Task to a Buffer (or vice-versa) "
  def __init__(self,lhs,rhs):
    self.lhs=lhs
    self.rhs=rhs
    self.is_reader=0
    self.is_writer=0
    if isinstance(lhs,Task):
      self.t=lhs
      self.b=rhs
      self.p=sonic.open_writer(lhs.t,rhs.b)
      self.is_writer=1
      lhs._writer_notify(self)
    else:
      self.t=rhs 
      self.b=lhs
      self.p=sonic.open_reader(rhs.t,lhs.b)
      self.is_reader=1
      rhs._reader_notify(self)
    self.b.append(self)
    self.id=sonic.pipe_id(self.p)
    log("Pipe.__init__(%s,%s)=%s"%(str(lhs),str(rhs),str(self)))
  def __repr__(self):
    return "Pipe(%s,%s)"%(str(self.lhs),str(self.rhs))
  def __str__(self):
    #if not self.p: return "p?"
    #return "p%d"%sonic.pipe_id(self.p)
    return "p%d"%self.id
  def info(self,depth):
    s = ""
    if self.is_reader:
      s += "  "*depth+"<size=%s"%self.read_size()
    #s = "%s: size=%s"%(repr(self),sz)
    rlimit = self.get_rlimit()
    if rlimit >= 0:
      s += " rlimit=%s"%(rlimit)
    if self.done():
      s += " done"
    if self.is_writer:
      s += " size=%s>\n"%self.write_size()
    return s
  def reset(self):
    sonic.pipe_reset(self.p)
  def send(self):
    return self.b.send()
  def pull(self):
    #if self.done():
      #return 0
    if self.is_reader:
      return self.b.pull()
    return self.t.pull()
  def push(self):
    #if self.done():
      #return 0
    if self.is_reader:
      return self.t.push()
    return self.b.push()
  def sources(self):
    assert self.is_reader
    return self.b.sources()
  def source(self):
    assert self.is_writer
    return self.t
  def targets(self):
    assert self.is_writer
    return self.b.targets()
  def target(self):
    assert self.is_reader
    return self.t
  def read_size(self):
    assert self.is_reader
    assert self.p
    return sonic.read_size(self.p)
  def write_size(self):
    assert self.is_writer
    assert self.p
    return sonic.write_size(self.p)
  def consume(self,i):
    assert self.is_reader
    assert self.p
    sonic.consume(self.p,i)
  def produce(self,i):
    assert self.is_writer
    assert self.p
    sonic.produce(self.p,i)
  def reader_mem(self):
    assert self.p
    return sonic.reader_mem(self.p)
  def writer_mem(self):
    assert self.p
    return sonic.writer_mem(self.p)
  def reader_request(self,size):
    assert self.p
    return sonic.reader_request(self.p,size)
  def writer_request(self,size):
    assert self.p
    return sonic.writer_request(self.p,size)
  def no_limit(self):
    assert self.p
    return sonic.pipe_no_limit(self.p)
  def rlimit(self,i):
    assert self.p
    return sonic.pipe_limit(self.p,sonic.pipe_get_i(self.p)+i)
  def limit(self,i):
    assert self.p
    return sonic.pipe_limit(self.p,i)
  def done(self):
    assert self.p
    return sonic.pipe_done(self.p)
  def get_i(self):
    assert self.p
    return sonic.pipe_get_i(self.p)
  def get_limit(self):
    assert self.p
    return sonic.pipe_get_limit(self.p)
  def get_rlimit(self):
    assert self.p
    return sonic.pipe_get_limit(self.p)-sonic.pipe_get_i(self.p)
  ##############################

  def read_short(self):
    assert self.read_size()>1
    x=sonic.ptrvalue(self.reader_mem(),0,"short")
    self.consume(2)
    assert type(x)==int
    return x
  def write_short(self,x):
    assert self.write_size()>1
    sonic.ptrset(self.writer_mem(),x,0,"short")
    self.produce(2)
  def __len__(self):
    if self.is_reader:
      return self.read_size()
    else:
      return self.write_size()
  ##############################

  def close(self):
    # needed when buffers are gc'ed before their tasks
    if sonic.is_reader(self.p):
      self.t.close_reader(self)
    else:
      self.t.close_writer(self)
  def free(self):
    assert self.p
    self.p=None
    self.lhs=None
    self.rhs=None
    self.b.remove(self)
    self.b=None
    self.t=None
    # note: pipes can't free themselves
  def pull_free(self):
    if self.is_reader:
      return self.b.pull_free()
    return self.t.pull_free()
  def pull_reset(self):
    if self.is_reader:
      count = self.b.pull_reset()
    else:
      count = self.t.pull_reset()
    self.reset()
    return 1+count
  def pull_visit(self):
    if self.is_reader:
      for x in self.b.pull_visit():
        yield x
    else:
      for x in self.t.pull_visit():
        yield x
    yield self
  def pull_str(self,depth=0):
    #s = [ "  "*depth+"%s\n"%self.info() ]
    s = [ "%s"%self.info(depth) ]
    if self.is_reader:
      s.append( self.b.pull_str(depth) )
    else:
      s.append( self.t.pull_str(depth+1) )
    return "".join(s)
  def __del__(self):
    log("Pipe.__del__(%s)"%str(self))
    if self.p:
      self.free();

def _find(name):
  if name:
    return eval( "sonic.task_%s_new"%name, globals(), {} )
  else:
    return sonic.task_new

############################################
#
#

class Task:
  """ Task objects process signals 
    obtained from Buffer objects (memory) 
    via Pipe objects (smart pointers)."""
  def __init__(self,name="none",*args):
    #print name,args
    #apply( PyTask.__init__, [self,name]+list(args))
    #if name is None:
      #name = "none"
    self.name=name
    self.args = []
    self.t = "??"
    log("Task.__init__(%s,%s)"%(name,args))
    self.args=args
    self.readers=[]
    self.writers=[]
    #print "len args",len(args)
    self.t = _find(name)( *args )
    self.id=sonic.task_id(self.t)
    self.mark=0 
    log("Task.__init__(%s,%s)=%s"%(name,args,self))
    #assert self.name
    #Task.tasks[self]=self
  #def getattr__(self,name):
    ##assert 0
    ##if name.startswith(
    #try:
      #f=eval( "sonic.task_%s_%s"%(self.name,name) )
      #return Func(f,self.t)
    #except Exception:
      #raise AttributeError
  def __repr__(self):
    assert self.t
    return "Task(%s)"%string.join([self.name]+map(str,self.args),",")
  def __str__(self):
    #if not self.t: return "t?"
    return "%s(t%s)"%(self.name,self.id)
  def _writer_notify(self,wp):
    self.writers.append(wp) 
  def _reader_notify(self,rp):
    self.readers.append(rp) 
  def reader(self):
    return self.readers[0]
  def writer(self):
    return self.writers[0]
  def _print(self):
    assert self.t
    sonic.task_print(self.t)
  def open_reader(self,buffer):
    return Pipe(buffer,self)
  def open_writer(self,buffer):
    return Pipe(self,buffer)
  def __ror__(self,x):
    b=Buffer()
    if type(x)==list:
      tree = x
      tree[-1:]=[Pipe(x[-1],b),Pipe(b,self),self]
    elif isinstance(x,Task):
      tree = [Pipe(x,b),Pipe(b,self),self]
    #elif isinstance(x,Buffer):
      #tree = [Pipe(x,self),self]
    else:
      raise TypeError, "Don't know how to connect to", other
    return tree
  def __call__(self, *args):
    tree = []
    for x in args:
      if isinstance(x, Task):
        x | self
      elif isinstance(x, Buffer):
        self.open_reader( x )
      else:
        raise TypeError, "Don't know how to connect to", x
    return self # XXX how to make this compatible with | ?
  def close_reader(self,p):
    assert self.t
    self.readers.remove(p)
    sonic.close_reader(self.t,p.p)
    p.free()
  def close_writer(self,p):
    assert self.t
    self.writers.remove(p)
    sonic.close_writer(self.t,p.p)
    p.free()
  def pipe(self,buf):
    return self.open_writer(buf)
  def _send(self):
    count=sonic.task_send(self.t)
    #print self.__class__.__name__,"_send",count
    #print "%s._send() == %s"%(self,count)
    return count
  def send(self):
    count=0
    for p in self.readers:
      p.send()
    count+=self._send()
    for p in self.readers:
      count+=p.send()
    for p in self.writers:
      count+=p.send()
    return count
  def pull(self):
    count=0
    for p in self.readers:
      count+=p.pull()
    count+=self._send()
    return count
  def push(self):
    count=self._send()
    for p in self.writers:
      count+=p.push()
    return count
  def pullpush(self):
    count=self.pull()
    for p in self.writers:
      count+=p.push()
    return count
  def sources(self):
    #print "%s.sources(): readers:"%self,self.readers
    #return reduce(lambda x,y:x+y,[p.sources() for p in self.readers],[])
    return [t for p in self.readers for t in p.sources() ]
  def source(self,*place):
    s=self
    for i in range(len(place)):
      s=s.sources()[place[i]]
    return s
  def targets(self):
    #print "%s.targets(): writers:"%self,self.writers
    #return reduce(lambda x,y:x+y,[p.targets() for p in self.writers],[])
    return [t for p in self.writers for t in p.targets() ]
  def target(self,*place):
    s=self
    for i in range(len(place)):
      s=s.targets()[place[i]]
    return s
  #def rotate_pull(self):
    #" when the path has loops "
    #queue=[self]
    #ready=[]
    #while queue:
      #t=queue.pop()
      #assert t.mark==0
      #t.mark=1
      #ready.append(t)
      #for _t in t.sources():
        #if not _t.mark:
          #queue.append(_t)
    #count=0
    #for t in ready:
      #t.mark=0
      #count+=t.send()
    #return count
  def pump(self):
    " when the path has loops "
    tank = {}
    queue = [self]
    while queue:
      _queue = []
      for task in queue:
        if not tank.has_key(task):
          tank[task] = 1
          _queue += task.sources()
      queue = _queue
    count = 0
    for task in tank.keys():
      _count = 1
      while _count:
        _count = task.send()
        count += _count
      #task.send()
    return count
  def reset(self):
    assert self.t
    sonic.task_reset(self.t)
  def done(self):
    assert self.t
    return sonic.task_is_done(self.t)
  def free(self):
    assert self.t
    log("task_free(%s)"%self)
    while self.readers: self.close_reader(self.readers[-1])
    while self.writers: self.close_writer(self.writers[-1])
    sonic.task_free(self.t)
    self.t=None
  def pull_free(self):
    count=0
    for p in self.readers[:]:
      count+=p.pull_free()
    self.free()
    return count+1
  def pull_reset(self):
    count=0
    for p in self.readers[:]:
      count+=p.pull_reset()
    self.reset()
    return count+1
  def pull_visit(self):
    for p in self.readers[:]:
      for x in p.pull_visit():
        yield x
    yield self
  def pull_str(self,depth=0):
    s = [ "  "*depth+"%s\n"%repr(self) ]
    for p in self.readers[:]:
      s.append( p.pull_str(depth+1) )
    return "".join(s)
  def __del__(self):
    log("Task.__del__(%s)"%str(self))
    if self.t: self.free()

############################################
#
#

class None_(Task):
  " None_: do nothing "
  def __init__(self):
    Task.__init__(self,"none")
class Null(Task):
  " Null(): trash all input "
  def __init__(self):
    Task.__init__(self,"null")
class Zero(Task):
  " write zero "
  def __init__(self):
    Task.__init__(self,"zero")
class Copy(Task):
  " copy input to output "
  def __init__(self):
    Task.__init__(self,"copy")
class Add(Task):
  " Add: output sum of all inputs "
  def __init__(self):
    Task.__init__(self,"add")
class Abs(Task):
  " output absolute value of input "
  def __init__(self):
    Task.__init__(self,"abs")
class RMod(Task):
  " output product of inputs "
  def __init__(self):
    Task.__init__(self,"rmod")
class RMod8(Task):
  " output product of inputs with 8 bit upshift"
  def __init__(self):
    Task.__init__(self,"rmod")
class Mean(Task):
  " output average of inputs "
  def __init__(self):
    Task.__init__(self,"mean")
class Mix(Task):
  " Mix(r=1.0): mix with gain=r "
  def __init__(self,r=1.0):
    Task.__init__(self,"mix",r)
    self.r=r
  def set_r(self,r):
    sonic.task_mix_set_r(self.t,r)
    self.r=r
  def get_r(self):
    return self.r
class Mix2(Task):
  def __init__(self):
    Task.__init__(self,"mix2")
class Mix4(Task):
  def __init__(self):
    Task.__init__(self,"mix4")
class Mix8(Task):
  def __init__(self):
    Task.__init__(self,"mix8")
class Fir(Task):
  " Fir(list_of_rs): generic finite impulse filter "
  def __init__(self,fir):
    sz=len(fir)
    _fir=sonic.ptrcreate("float",0,sz)
    for i in range(len(fir)):
      sonic.ptrset(_fir,fir[i],i,"float")
    Task.__init__(self,"fir",_fir,sz)
    sonic.ptrfree(_fir)
class Resample(Task):
  " Resample(r): resample at rate r "
  def __init__(self,r):
    Task.__init__(self,"resample",r)
    self.r = r
  def set_r(self,r):
    sonic.task_resample_set_r(self.t,r)
    self.r = r
  def get_r(self):
    return self.r
class Split(Task):
  " output left and right from stereo (interleaved) input "
  def __init__(self):
    Task.__init__(self,"split")
class Interleave(Task):
  " output stereo (interleaved) from left and right inputs "
  def __init__(self):
    Task.__init__(self,"interleave")
class Gain(Task):
  " Gain(r=1.0): ouptput input multiplied by r "
  def __init__(self,r=1.0):
    Task.__init__(self,"gain",r)
    self.r=r
  def set_r(self,r):
    sonic.task_gain_set_r(self.t,r)
    self.r=r
  def get_r(self):
    return self.r

class File(Task):
  " File(filename,mode): read a file "
  def __init__(self,filename,mode="r"):
    if mode == "r":
      self.sz=os.stat(filename)[6]
      Task.__init__(self,"file_rd",filename)
    elif mode == "w":
      Task.__init__(self,"file_wr",filename)
    else:
      raise Exception, "invalid mode"
  def size(self):
    return self.sz
  def seek(self,offset):
    r=sonic.task_fd_seek(self.t,offset)
    log("FileRd.seek(%s)"%r)
    assert r==offset
class FileRd(File):
  " FileRd(filename): read a file "
  def __init__(self,filename):
    File.__init__(self,filename,"r")
class FileWr(File):
  " FileWr(filename): write a file "
  def __init__(self,filename):
    File.__init__(self,filename,"w")

#class OSSRdWr(Task):
  #" DspRdWr(dev,speed,stereo): read/write soundcard "
#class OSSRd(Task):
  #" DspRd(dev,speed,stereo): read soundcard "
#class OSSWr(Task):
  #" DspWr(dev,speed,stereo): write soundcard "

class OSS(Task):
  " OSS(dev,speed,stereo,mode='w'): read/write OSS soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2],mode="w"):
    if mode == "w":
      task_name = "dsp_wr"
    elif mode == "r":
      task_name = "dsp_rd"
    elif mode == "rw":
      task_name = "dsp_rdwr"
    else:
      raise Exception, "invalid mode"
    Task.__init__(self,task_name,dev,speed,stereo)
    self.dev = dev
    self.speed = speed
    self.stereo = stereo
class OSSRd(OSS):
  " OSSRd(dev,speed,stereo): read OSS soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2],chn=None):
    OSS.__init__(self,dev,speed,stereo,"r")
    if chn is not None:
      self.set_recsrc( chn )
  def set_recsrc(self, chn):
    sonic.set_recsrc(self.dev,chn)
class OSSWr(OSS):
  " OSSWr(dev,speed,stereo): write OSS soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2]):
    OSS.__init__(self,dev,speed,stereo,"w")
class OSSRdWr(OSSRd,OSSWr):
  " OSSRdWr(dev,speed,stereo): read/write OSS soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2]):
    OSS.__init__(self,dev,speed,stereo,"rw")

class PA(Task):
  " PA(dev,speed,stereo,mode, frames_per_buffer ): read/write portaudio soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2],mode="w", fpb=fpb):
    self.dev = dev
    self.speed = speed
    self.stereo = stereo
    if mode == "w":
      ichans = 0
      ochans = stereo + 1
      cb = self.pull # pump ?
    elif mode == "r":
      ichans = stereo + 1
      ochans = 0
      cb = self.push # pump ?
    elif mode == "rw":
      ichans = stereo + 1
      ochans = stereo + 1
      cb = self.pullpush # pump ?
    else:
      raise Exception, "invalid mode"
    #Task.__init__(self,"portaudio",cb,None,ichans,ochans,fpb,dev,speed)
    Task.__init__(self,"portaudio",ichans,ochans,fpb,dev,speed)
  def start(self, cb, args=None):
    sonic.task_portaudio_start( self.t, cb, args ) # starts portaudio thread
  def stop(self):
    sonic.task_portaudio_stop( self.t ) # stops portaudio thread
class PARdWr(PA):
  " PARdWr(dev,speed,stereo): read/write portaudio soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2], fpb=fpb):
    PA.__init__(self,dev,speed,stereo,"rw")
class PARd(PA):
  " PARd(dev,speed,stereo): read portaudio soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2], fpb=fpb):
    PA.__init__(self,dev,speed,stereo,"r")
class PAWr(PA):
  " PAWr(dev,speed,stereo): write portaudio soundcard "
  def __init__(self,dev=dsp[0],speed=dsp[1],stereo=dsp[2], fpb=fpb):
    PA.__init__(self,dev,speed,stereo,"w")
del dsp

print "using soundcard driver", soundcard
if soundcard == "OSS":
  _Dsp,_DspRdWr,_DspRd,_DspWr=OSS,OSSRdWr,OSSRd,OSSWr
elif soundcard == "portaudio":
  _Dsp,_DspRdWr,_DspRd,_DspWr=PA,PARdWr,PARd,PAWr
else:
  raise Exception, "please define soundcard in .hypersonicrc file"

class Dsp(_Dsp):
  " DspRdWr(dev,speed,stereo): read/write soundcard "
  pass
class DspRdWr(_DspRdWr):
  " DspRdWr(dev,speed,stereo): read/write soundcard "
  pass
class DspRd(_DspRd):
  " DspRd(dev,speed,stereo): read soundcard "
  pass
class DspWr(_DspWr):
  " DspWr(dev,speed,stereo): write soundcard "
  pass

del soundcard

class Sin(Task):
  " Sin(f=440,r=1.0): generate a sin wave, freq=f, amplitude=r "
  def __init__(self,f=440.0,r=1.0):
    self.f=f
    self.r=r
    Task.__init__(self,"sin",f,r)
  def set_f(self,f):
    self.f=f
    sonic.task_sin_set_f(self.t,f)
  def set_r(self,r):
    self.r=r
    sonic.task_sin_set_r(self.t,r)
class Squ(Task):
  " Squ(f=440,r=1.0): generate a square wave "
  def __init__(self,f=440.0,r=1.0):
    self.f=f
    self.r=r
    Task.__init__(self,"squ",f,r)
  def set_f(self,f):
    self.f=f
    sonic.task_squ_set_f(self.t,f)
  def set_r(self,r):
    sonic.task_squ_set_r(self.t,r)
    self.r=r
class Tri(Task):
  " Tri(f=440,r=1.0): generate a triangle wave "
  def __init__(self,f=440.0,r=1.0):
    self.f=f
    self.r=r
    Task.__init__(self,"tri",f,r)
  def set_f(self,f):
    self.f=f
    sonic.task_tri_set_f(self.t,f)
  def set_r(self,r):
    sonic.task_tri_set_r(self.t,r)
    self.r=r
class Noise(Task):
  " Noise(): generate noise "
  def __init__(self):
    Task.__init__(self,"noise")
class Lo(Task):
  " Lo(r): low pass filter "
  def __init__(self,r):
    Task.__init__(self,"lo",r)
  def set_r(self,r):
    sonic.task_lo_set_r(self.t,r)
class RLo1(Task):
  " RLo1(f,r): resonant low pass filter (1) "
  def __init__(self,f=440,r=0.97):
    Task.__init__(self,"rlo1",f,r)
  def set_f(self,f):
    sonic.task_rlo1_set_f(self.t,f)
  def set_r(self,r):
    sonic.task_rlo1_set_r(self.t,r)
class RLo2(Task):
  " RLo2(f,r): resonant low pass filter (2) "
  def __init__(self,f,r):
    Task.__init__(self,"rlo2",f,r)
  def set_f(self,f):
    sonic.task_rlo2_set_f(self.t,f)
  def set_r(self,r):
    sonic.task_rlo2_set_r(self.t,r)
class Hi(Task):
  " Hi(r): hi pass filter "
  def __init__(self,r):
    Task.__init__(self,"hi",r)
class Env(Task):
  " Env(): max abs of each block read "
  def __init__(self):
    Task.__init__(self,"env")
class RMS(Task):
  " RMS(): root mean square over each block read "
  def __init__(self):
    Task.__init__(self,"rms")

class Tap:
  def __init__(self,tp):
    self.tp=tp
  def set_i(self,i):
    sonic.tap_set_i(self.tp,i)
  def set_r(self,r):
    x=int(r*SMAX)
    sonic.tap_set_x(self.tp,x)
class IIR(Task):
  " IIR(line=[]): infinite impulse response filter "
  def __init__(self,line=[]):
    Task.__init__(self,"iir")
    self.line=[]
    for i,r in line:
      self.add(i,r)
  def __len__(self):
    return len(self.line)
  def __getitem__(self,idx):
    return self.line[idx][2]
  def add(self,i,r):
    assert -1.0 <= r <= 1.0
    x=int(r*SMAX)
    log("iir_add %d %d",i,x)
    tp=Tap( sonic.task_iir_add(self.t, i, x) )
    self.line.append((i,x,tp))
    return tp

class Delay(Task):
  " Delay(n): output is n samples behind input "
  def __init__(self, n, fill = True):
    Task.__init__(self,"delay",n)
    self.n=n
    if fill:
      # fill with zeros 
      p = pipe( Zero(), Buffer(), self )[-1]
      while self.pull():
        pass
      p.close()
  def set_n(self,n):
    sonic.task_delay_set_n(self.t,n)
    self.n=n
    log("delay=%s"%n)
class Trace(Task):
  " Trace(x,y,w,h): SDL graphical display of signal "
  def __init__(self,x=0,y=0,w=640,h=480):
    Task.__init__(self,"trace",x,y,w,h)
class Lookup(Task):
  " Lookup(buf=None): use input as index into values in buf"
  def __init__(self,b=None):
    if b==None:
      b=Buffer( 1<<17 )
      b.fill( Sin(1.0) )
    Task.__init__(self,"lookup",b.b)
    self.lookup_buf = b # incref
  def flush(self):
    sonic.task_lookup_flush(self.t)

class Linear(Task):
  """ Linear(v,x_init=0): linear spline, 
    v is a list of (width,level) pairs """
  def __init__(self,v,x_init=0):
    self.v=[]
    Task.__init__(self,"linear",len(v),x_init)
    for di,x in v:
      self.append(di,x)
  def __str__(self):
    return "Linear(%s)"%self.v
  def __setitem__(self,idx,val):
    #log("Linear.__setitem__(%s,%s)"%(idx,val))
    #if type(idx)==SliceType:
      ##log(str((idx.start,idx.stop)))
      #i=0
      #while i<len(val):
       #  TOO HARD
      #for i in range(idx.start,min(idx.stop,len(val))):
        #self[i]=val[i-idx.start]
    #else:
      #log(" self.v[%s]=%s"%(idx,val))
      assert val[0]>0
      self.v[idx]=val
      sonic.task_linear_setitem(self.t,idx,val[0],val[1])
  def __len__(self):
    return len(self.v)
  def __getitem__(self,idx):
    return self.v[idx]
  def append(self,di,x):
    self.v.append((di,x))
    sonic.task_linear_append(self.t,di,x)
  def pop(self):
    sonic.task_linear_pop(self.t)
    return self.v.pop()
  def update(self,l):
    assert( len(l) == len(self) )
    for i in range(len(l)):
      #self[i]=l[i] # too slow !
      self.v[i]=l[i]
      sonic.task_linear_setitem(self.t,i,l[i][0],l[i][1])

class Term(Task):
  """ Term(cb=None): ncurses interface, outputs keypresses,\
 behaves like a dict of lines: term[0]="foo" """
  def __init__(self,cb=lambda x:None):
    set_log( open("logfile.out","w") )
    Task.__init__(self,"term")
    if sys.stderr.fileno() == 2:
      sys.stderr.close()
    sys.stderr=open("errlog","w")
    self.lines={}
    self.nline=1
    #self.ibuf=Buffer(128)
    #Pipe(self,self.ibuf)
    #self.ipipe=Pipe(self,self.ibuf)
    #self.cb=cb
  def __del__(self):
    sys.stderr=sys.stdout
    #self.ibuf.free()
    #del self.ibuf
    #del self.ipipe
    #Task.__del__(self)
  def __setitem__(self,key,s):
    try:
      i=int(key)
    except ValueError:
      try:
        i=self.lines[key]
      except KeyError:
        i=self.nline+1
      self.lines[key]=i
    self.nline=max(self.nline,i)
    sonic.task_term_set_line(self.t,i,s)
class GetChar(Task):
  def __init__(self,cb=lambda x:None,*data):
    Task.__init__(self,"none")
    self.cb=cb
    self.data=list(data)
  def get_char(self,rp):
    #log("Pipe.get_char(%s) read_size=%s"%(self,self.read_size()))
    sz=rp.read_size()
    if sz:
      rmem=rp.reader_mem()
      s=""
      log("rmem = ",rmem)
      for i in range(sz):
        c=sonic.ptrvalue(rmem,i,"char")[0] # [0] discards junk ...
        s=s+c
      rp.consume(sz)
      return string.join(s)
    return None
  def send(self):
    #log("GetChar.send %s "%self.reader)
    count=Task.send(self)
    #return count
    for rp in self.readers:
      s=self.get_char(rp)
      if s:
        apply( self.cb, [s]+self.data )
        count+=1
    return count
class GetInt(Task):
  def __init__(self,cb=lambda x:None,*data):
    Task.__init__(self,"none")
    self.cb=cb
    self.data=list(data)
  def get_int(self,rp):
    #log("Pipe.get_int(%s) read_size=%s"%(self,self.read_size()))
    sz=rp.read_size()
    if sz:
      rmem=rp.reader_mem()
      s=sonic.ptrvalue(rmem,0,"char")[:]
      #print s
      rp.consume(sz)
      try:
        return int(s)
      except ValueError:
        return None
    return None
  def send(self):
    count=Task.send(self)
    #return count
    #log("GetChar.send %s "%self.readers)
    for rp in self.readers:
      i=self.get_int(rp)
      if i is not None:
        apply( self.cb, [i]+self.data )
        count+=1
    return count

def free_garbage():
  gc.collect()
  #print " gc list ",gc.garbage
  count=0
  for x in gc.garbage[:]:
    if isinstance(x,Task):
      x.free()
      #gc.garbage.remove(x)
      count+=1
    elif isinstance(x,Buffer):
      x.free()
      #gc.garbage.remove(x)
      count+=1
  gc.garbage[:]=[]
  log( "free_garbage(): %d freed"%count )
    
#B=Buffer
#T=Task
#P=Pipe

outstr={}
def output(s):
  global outstr
  #log(outstr)
  if not outstr:
    log("   ------------------- begin log ------------------- ")
  if not outstr.has_key(s):
    log("  "+s)
    outstr[s]=1
  elif len(outstr.keys())>2:
    log("  "+s)
    outstr={s:1}
#def output(s):
  #log(s)

if 0:
  try:
    import psyco
  except ImportError:
    pass

def pipe(*args):
  pipes = []
  t = None
  b = None
  for x in args:
    if isinstance(x,Task):
      t = x
      if b:
        pipes.append( Pipe(b,t) )
        b = None
      #else:
        #pipes.append(None) # as a warning
    elif isinstance(x,Buffer):
      b=x
      if t:
        pipes.append( Pipe(t,b) )
        t = None
      #else:
        #pipes.append(None) # as a warning
    else:
      raise TypeError, x
  if len(pipes)==1:
    return pipes[0]
  return pipes
connect = pipe
#join = pipe

def join(*args,**kwargs):
  #_bufsz = bufsz
  _bufsz = None
  if kwargs.has_key( "bufsz" ):
    _bufsz = kwargs[ "bufsz" ]
  pipes = []
  t = None
  b = None
  for x in args:
    if isinstance(x,Task):
      if b is None and t is not None:
        if _bufsz is not None:
          b = Buffer(_bufsz)
        else:
          b = Buffer()
        #assert t is not None
        print "t -> Buffer()",
        pipes.append( Pipe( t,b ) )
      t = x
      if b is not None:
        print "b->t",
        pipes.append( Pipe(b,t) )
        b = None
    elif isinstance(x,Buffer):
      if t is None and b is not None:
        t = Copy()
        #assert b is not None
        print "b -> Copy()",
        pipes.append( Pipe( b,t ) )
      b=x
      if t is not None:
        print "t->b",
        pipes.append( Pipe(t,b) )
        t = None
    else:
      raise TypeError, x
  print
  if len(pipes)==1:
    return pipes[0]
  return pipes

#
#
########################################################

class Loop(Task):
  """ Loop(filename)
  Loop(array,sz=None)
  Loop(mem,sz) """ 
  def __init__(self,*args):
    if len(args) == 1 and type(args[0]) == str:
      fnam=args[0]
      self.array=MMap(fnam)
      mem=self.array.mem
      sz=self.array.sz # bytecount
    elif args and isinstance(args[0],Array):
      self.array = args[0]
      sz=self.array.sz # bytecount
      if len(args)>1 and type(args[1])==int:
        sz=args[1] 
        assert 0<=sz<=self.array.sz
      mem = self.array.mem
    elif len(args)==2:
      mem,sz=args # deprecated
    else:
      raise TypeError, args
    #print mem,sz
    self.mem=mem
    self.sz=sz
    Task.__init__(self,"loop",mem,sz)
  #def _send(self):
    #print "loop offset",self.get_offset()
    #return Task._send(self)
  def seek(self,offset):
    " offset is bytecount "
    offset %= self.sz
    assert 0<=offset<self.sz
    sonic.task_mem_seek(self.t,offset)
  def get_offset(self):
    return sonic.task_mem_get_offset(self.t)
  def clone(self):
    return Loop(self.mem,self.sz)

class MemTask(Task):
  def __init__(self,name,array,sz):
    if sz is None:
      self.sz=self.array.sz
    else:
      self.sz=sz
      assert 0 <= sz <= self.array.sz
    Task.__init__(self,name,array,sz)
    self.array=array
  def seek(self,offset):
    " offset is bytecount "
    assert 0<=offset<self.sz
    sonic.task_mem_seek(self.t,offset)
  def get_offset(self):
    return sonic.task_mem_get_offset(self.t)
  def clone(self):
    return self.__class__(self.array,self.sz)

class MemRd(MemTask):
  def __init__(self,array,sz=None):
    MemTask.__init__(self,"mem_rd",array,sz)

class MemWr(MemTask):
  def __init__(self,array,sz=None):
    MemTask.__init__(self,"mem_wr",array,sz)

#
##########################

class Array:
  def __init__(self,sz,itemsz=1):
    "sz is byte count"
    self.a=sonic.array_new(sz)
    self.sz=sonic.array_sz(self.a) # bytecount
    self.mem=sonic.array_mem(self.a)
    self.itemsz=itemsz # used for indexing
    log(self)
  def free(self):
    sonic.array_free(self.a)
    self.a=None
  def __str__(self):
    return "Array(%d)"%self.sz
  def __del__(self):
    log("__del__(%s)"%str(self))
    if self.a: 
      self.free()
  def __getitem__(self,i,value):
    if i<0 or i>=self.sz/2: # itemsz XXX
      raise IndexError(i)
    #return sonic.ptrvalue(self.mem,i,"short")
    return sonic.array_get_short(self.a,i) # XXX
  def __setitem__(self,i,value):
    if i<0 or i>=self.sz/2: # XXX
      raise IndexError(i)
    #sonic.ptrset(self.mem,value,i,"short")
    sonic.array_set_short(self.a,i,value) # XXX
    #log("__setitem__(%s,%s,%s)"%(self,i,value))
  #def loop(self,sz=None): # bytecount
    #if sz is None:
      #sz=self.sz
    ##t= Task("loop",self.mem,sz*self.item_len)
    #t=Loop(self.mem,sz)
    #t._a=self # incref self
    #return t
class MMap(Array):
  def __init__(self,filename):
    self.filename=filename
    self.a=sonic.array_new_mmap(filename)
    self.sz=sonic.array_sz(self.a)
    self.mem=sonic.array_mem(self.a)
  def __str__(self):
    return "MMap('%s',%d)"%(self.filename,self.sz)
  #def __str__(self):
    #return "MMap(%s)=a?"%self.filename
class SubArray(Array):
  def __init__(self,array,start,end):
    self.a=sonic.array_new_sub(array.a,start,end)
    self.mem=sonic.array_mem(self.a)
    self.sz=sonic.array_sz(self.a)
  def __str__(self):
    return "SubArray(%s,start=%d,end=%d)"\
      %(self.a,self.start,self.end)
class ShortArray(Array):
  def __init__(self,sz):
    "sz is short count"
    Array.__init__(self,sz*2,itemsz=2)
     
class Wavetable(ShortArray):
  " build from callable on 0<=x<1 "
  def __init__(self,func,dx):
    N = int(1.0/dx)
    ShortArray.__init__(self,N)
    x = 0.0
    i = 0
    while i<N:
      self[i] = func(x)
      x+=dx
      i+=1

def mkloop(func,dx):
  return WaveTable(func,dx).loop()

#
#
########################################################

def ftos(f):
  return 44100.0 / f

#
#
########################################################

#MSG_LEN=128
#def mk_msg():
  #s=sonic.xcalloc(MSG_LEN)
  #return s
#def c2py(s,n):
  #return string.join( map(lambda x:sonic.xchar(s,x),range(n)), "")
#def get_msg(s):
  #return c2py(s,MSG_LEN)
#def free_msg(s):
  #sonic.xfree(s)

def _print(x): log(x)
#class ReadMsg(Task):
  #def __init__(self,cb=_print):
    #Task.__init__(self,"none")
    #self.cb=cb
  #def send(self):
    #count=0
    ##log("send")
    #if self.readers:
      #rp=self.readers[0]
      #while 1:
        #msg=" "*MSG_LEN
        ##log(repr(msg))
        #i=sonic.read_msg(rp.p,msg,MSG_LEN)
        #if not i: break
        #if i==1: i=i+1
        #self.cb( float( msg[:i-1] ))
        #count+=1
    #return count



if __name__=="__main__":
  l=dir(sonic)
  log(reduce( lambda x,y:x+" "+y, l ))

