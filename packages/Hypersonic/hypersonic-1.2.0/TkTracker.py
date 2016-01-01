#!/usr/bin/env python

from __future__ import nested_scopes

import sys
from time import *
from Tracker import *
from Tkinter import *

try:
  import psyco
  psyco.full()
except:
  pass

from ps import *



class TkTracker:
  def __init__(self,root,tracker,filename="noname.aupy"):
    self.root = root
    self.tracker = tracker # model
    self.offset = 0 # pixels
    #############################
    top = Frame(root)
    top.pack(side=TOP)
    klass = self.__class__
    b=Button( top, text = "|<", command = self.initial )
    b.pack( side=LEFT )
    b=Button( top, text = "<<", command = self.big_prev )
    b.pack( side=LEFT )
    b=Button( top, text = "<", command = self.prev )
    b.pack( side=LEFT )
    b=Button( top, text = ">", command = self.next )
    b.pack( side=LEFT )
    b=Button( top, text = ">>", command = self.big_next )
    b.pack( side=LEFT )
    #b=Button( top, text = ">|", command = self.final )
    #b.pack( side=LEFT )
    for s in ["start","stop","zoom_in","zoom_out",
      "_print", "custom"]:
      b=Button( top, text = s, command = getattr(self,s) )
      b.pack(side=LEFT)
      #Label(top,text="  ").pack(side=LEFT)
    #############################
    self.rec_entry=Entry(top,width=24)
    self.rec_entry.insert(END,"noname.raw")
    self.rec_entry.bind("<Return>",self.rec)
    self.rec_entry.pack(side=RIGHT)
    Button(top,text="rec",command=self.rec).pack(side=RIGHT)
    #############################
    self.save_entry=Entry(top,width=24)
    self.save_entry.insert(END,filename)
    self.save_entry.bind("<Return>",self.save)
    self.save_entry.pack(side=RIGHT)
    Button(top,text="save",command=self.save).pack(side=RIGHT)
    #############################
    self.dy=15 # pixels per track
    self.dx=1 # pixels per block (=4096 frames)
    #self.dx=500
    width,height=2*512,max(64,self.dy*len(tracker))
    hfram = Frame(root)
    hfram.pack(side=TOP)
    bot=Frame(root)
    bot.pack(side=TOP)
    vscroll=Scrollbar(hfram)
    hscroll=Scrollbar(bot,orient=HORIZONTAL)#,width=width)
    sheet = Canvas(
      hfram,width=width,height=height, bg="white",
      yscrollcommand=vscroll.set,
      xscrollcommand=hscroll.set )
    sheet.pack(side=LEFT)
    vscroll.config(command=sheet.yview)
    hscroll.config(command=sheet.xview)
    #vscroll.pack(side=LEFT,fill=BOTH)
    #hscroll.pack(side=BOTTOM,fill=BOTH)
    sheet.bind( "<Button-1>",self.button1)
    sheet.bind( "<B1-Motion>",self.button1)
    #sheet.bind( "<Button-2>",self.button2)
    #sheet.bind( "<B2-Motion>",self.button2_motion)
    sheet.bind( "<Button-3>",self.button3)
    sheet.bind( "<B3-Motion>",self.button3)
    #############################
    self.sheet=sheet
    #############################
    self.paint()
  #######################################

  def rect(self,tracki,i):
    y = tracki * self.dy
    track = self.tracker[tracki]
    sz = track.frames/4096.0
    #x = i*self.dx*sz - (self.offset % (self.dx*sz)) 
    x = i*self.dx*sz - self.offset 
    val = track[i]
    if val > 0.0:
      fill = "black"
    else:
      fill = "white"
    id = self.sheet.create_rectangle(
      x, y, x+self.dx*sz-1, y+self.dy-1, fill=fill, outline="red" )

  def ps_rect(self,ps,tracki,i):
    y = (len(self.tracker)-tracki) * self.dy
    track = self.tracker[tracki]
    sz = track.frames/4096.0
    #x = i*self.dx*sz - (self.offset % (self.dx*sz)) 
    x = i*self.dx*sz - self.offset 
    val = track[i]
    if val > 0.0:
      s = Fill()
      s.rect( x, y, x+self.dx*sz-1, y+self.dy-1 )
    else:
      s = Stroke()
      s.rect( x, y, x+self.dx*sz-1, y+self.dy-1 )
    ps(s)

  def find_closest(self,x,y):
    #_tracki, _i = self._find_closest(x,y)
    tracki = int(y // self.dy)
    tracki = min( tracki, len(self.tracker)-1 )
    tracki = max( tracki, 0 )
    track = self.tracker[tracki]
    sz = track.frames/4096.0
    _dx = self.dx*sz # width of these bricks
    i = ((x+self.offset)//_dx)
    #i = max( 0, min( len(track), i ) )
    #assert _tracki == tracki
    #print _tracki - tracki, i - _i
    return tracki, int(i)

  def paint(self):
    print "paint"
    self.sheet.delete(ALL)
    width = int(self.sheet["width"])
    for tracki in range(len(self.tracker)):
      track = self.tracker[tracki]
      sz = track.frames/4096.0
      _dx = self.dx*sz # width of these bricks
      x = -(self.offset % _dx)
      i = int(self.offset // _dx)
      while x < width:
        self.rect( tracki, i )
        x += 8*_dx
        i += 8*1
      for i,val in track.items():
        x = i*self.dx*sz - self.offset
        if 0 <= x < width:
          self.rect( tracki, i )

  def custom(self):
    print "custom"
    width = int(self.sheet["width"])
    for tracki in range(len(self.tracker)):
      track = self.tracker[tracki]
      sz = track.frames/4096.0
      _dx = self.dx*sz # width of these bricks
      x = -(self.offset % _dx)
      i = int(self.offset // _dx)
      while x < width:
        self.tracker[tracki][i] = 1.0 # set
        self.rect( tracki, i )
        x += 8*_dx
        i += 8*1

  def ps_paint(self):
    print "ps_paint"
    offset = 0
    page = 0
    while 1:
      print "page %d...."%page
      ps = PS()
      ps.setlinewidth(1)
      width = int(self.sheet["width"])
      more = 0
      for tracki in range(len(self.tracker)):
        track = self.tracker[tracki]
        sz = track.frames/4096.0
        _dx = self.dx*sz # width of these bricks
        x = -(offset % _dx)
        i = int(offset // _dx)
        while x < width:
          self.ps_rect( ps, tracki, i )
          #x += 8*_dx
          #i += 8*1
          x += _dx
          i += 1
        #for i,val in track.items():
          #x = i*self.dx*sz - offset
          #if 0 <= x < width:
            #more += 1
            #self.ps_rect( ps, tracki, i )
      ps.write( "score.%.2d.ps"%page ) 
      if not more:
        break
      offset += 512
      page += 1
  #######################################

  def button1(self,event):
    can = event.widget
    x = can.canvasx(event.x)
    y = can.canvasy(event.y)
    tracki, i = self.find_closest(x,y)
    if event.state & 1:
      print "shift"
      self.rect( tracki, i )
      self.tracker.play1(tracki)
    elif event.state & 4:
      print "ctrl"
      self.tracker[tracki].bump(-1)
      for i in self.tracker[tracki].keys():
        self.rect( tracki, i )
        self.rect( tracki, i-1 )
        self.rect( tracki, i+1 )
    else:
      self.tracker[tracki][i] = 1.0
      self.rect( tracki, i )
  #def button2(self,event):
    #self.scan_y=event.y
    #can=event.widget
    #can.scan_mark(event.x,event.y)
  #def button2_motion(self,event):
    #can=event.widget
    #can.scan_dragto(event.x,self.scan_y)
  def button3(self,event):
    can = event.widget
    x = can.canvasx(event.x)
    y = can.canvasy(event.y)
    tracki, i = self.find_closest(x,y)
    if event.state & 1:
      print "shift"
    elif event.state & 4:
      print "ctrl"
      self.tracker[tracki].bump(1)
      for i in self.tracker[tracki].keys():
        self.rect( tracki, i )
        self.rect( tracki, i-1 )
        self.rect( tracki, i+1 )
    else:
      self.tracker[tracki][i] = 0.0
      self.rect( tracki, i )
  #######################################

  def initial(self):
    if self.offset == 0:
      return
    self.offset = 0
    self.paint()
  def big_prev(self):
    if self.offset == 0:
      return
    self.offset = max(0,self.offset-512)
    self.paint()
  def prev(self):
    #print "prev"
    if self.offset == 0:
      return
    self.offset = max(0,self.offset-128)
    self.paint()
  def next(self):
    #print "next"
    self.offset += 128
    self.paint()
  def big_next(self):
    self.offset += 512
    self.paint()
  def final(self):
    pass
  def _print(self):
    #self.sheet.postscript( file = "score.ps" )
    self.ps_paint()
  def save(self,ev=None):
    fnam=self.save_entry.get()
    if not fnam:
      fnam = "tktracker.aupy"
    print "save",fnam
    f=file(fnam,"w")
    f.write(repr(self.tracker))
    f.close()
  def rec(self):
    fnam = self.rec_entry.get()
    if not fnam:
      fnam = "tktracker.raw"
    print "rec",fnam
    self.tracker.rec(fnam)
  def zoom_in(self):
    print "zoom_in"
    self.dx=(self.dx*1.3)
    self.paint()
  def zoom_out(self):
    print "zoom_out"
    self.dx=max(1,(self.dx/1.3))
    self.paint()
  def start(self):
    print "start"
    #if self.cb:
      #self.stop()
      #return
    self.tracker.start( offset = 4096 * self.offset / self.dx )
    #print "start: cb=",cb
    #self.send()
  def stop(self):
    print "stop"
    self.tracker.stop()
    #self.cb=None
  #def add(self):
    #print "add"


#from random import *
#seed(0)
def mktracker(files):
  tracks=[]
  n=4
  tracki=0
  for f in files:
    track=Track( f, tracki=tracki ) 
    tracks.append( track )
    tracki+=1
  #for track in tr:
    #print track
    #track[ randrange(len(track)) ] = 1.0
  #tracks.sort( lambda a,b:a.frames-b.frames )
  tr=Tracker(tracks)
  #s = repr(tr)
  #sleep(1)
  #tr = eval(s)
  return tr

def test1(files):
  tr=Tracker()
  n=4
  for f in files:
    mm=MMap(f)
    track=Track(mm.loop(),8) 
    tr.append( track )
  for track in tr:
    print track
    track[ randrange(n) ] = 1.0
  tr.start()
  while tr.send():
    for track in tr:
      track.send()
  tr.stop()
  sleep(1)

def from_raw(files):
  root=Tk()
  #tr=Tracker()
  tr = mktracker(files)
  tkt = TkTracker(root,tr)
  try:
    root.mainloop()
  except KeyboardInterrupt:
    pass
  tr.free()

def from_file(dfile):
  f=open(dfile)
  tr = eval( f.read() )
  root=Tk()
  TkTracker(root,tr,filename=dfile)
  try:
    root.mainloop()
  except KeyboardInterrupt:
    pass
  tr.free()

def do_it():
  tr = eval( f.read() )
  root=Tk()
  tkt = TkTracker(root,tr)
  for i in range(2):
    tkt.start()
    tkt.stop()
  tr.free()

def prof(dfile):
  global f
  import profile
  f=open(dfile)
  #profile.run( "do_it()", 'profile.out' )
  do_it(); return
  profile.run( "do_it()" )
  #stats = profile.Stats( 'profile.out' )
  #stats.print_stats()
  tr.free()

files = sys.argv[1:]

if __name__=="__main__":
  xmark()
  if not files:
    prof("noname2.aupy")
  elif files[0].endswith("aupy"):
    from_file(files[0])
  else:
    from_raw(files)
  free_garbage()
  xcheck()




