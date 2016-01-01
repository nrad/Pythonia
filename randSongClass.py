from music21 import *
from circOfFifth import *
environment.set("musicxmlPath", "/usr/bin/musescore")
from random import *
'''
sBach = corpus.parse('bach/bwv7.7')
>>> n1 = note.Note('e4')
>>> n1.duration.type = 'whole'
>>> n2 = note.Note('d4')
>>> n2.duration.type = 'whole'
>>> m1 = stream.Measure()
>>> m2 = stream.Measure()
>>> m1.append(n1)
>>> m2.append(n2)
>>> partLower = stream.Part()
>>> partLower.append(m1)
>>> partLower.append(m2)
>>> partLower.show()  
'''

#notes=('c','db','d','eb','e','f','gb','g','ab','a','bb','b')



def randwWeight(lis):
  distlist=[]
  for val, weight in lis:
    for i in range (0,weight):
      distlist.append(val)

  #print distlist
  return sample(distlist,1)


#majScale=(0, 2, 4, 5, 7, 9, 11, 12)
#minScale=(0, 2, 3, 5, 7, 8, 10, 12)




notewithpitch='{0}{1}'.format(notes[0],4)
fscale = majScale

fScaleW = [(0,10), (2,1),(4,1) ,(5,5) ,(7,10) ,(9,1),(11,1),(12,10)]
ffScaleW = [(0,10), (2,1),(3,5) ,(5,5) ,(7,10) ,(8,1),(11,1),(12,10)]


nMeasures = 20
lenMeasure = 4
nNotes =len(fscale)
ckey = 'c'

measures={}
fnoteDur = durations['0.25']

measDur = randint(0,len(durations))

noteDurs=[0.25,0.5,1]
noteDursWeight=[(0.25,2),(.5,10),(1,10),(4,1)]





class randSong:
  def __init__(self,nMeasures,key):
    debug=0
    stayInKey=1
    if not stayInKey : ntTMP=key

    self.mDict={}
    for iM in range(0,nMeasures):
      self.mDict[iM]=[]

      mLen=0
      while mLen < lenMeasure:
        #ntDur = sample(noteDurs,1)[0]
        ntDur = randwWeight(noteDursWeight)[0]

        if mLen + ntDur > lenMeasure:
          ntDur = lenMeasure - mLen
          while ntDur not in noteDurs:
            ntDur -= noteDurs[0]
            if debug: print 'BEING SUBTRACTED', ntDur

        mLen = mLen + ntDur
        #nt= harmony(key,fscale[randint(0,6)])
        if stayInKey:
          sign = eval(choice('+-')+str(1))
          nt = harmony(key,sign*randwWeight(fScaleW)[0])
        if not stayInKey:
          intv = randwWeight(fScaleW)[0]
          nt = harmony(ntTMP,intv)
          print "&&&&&&&&&&&&&&", ntTMP ,nt , '%%%%%%%', intv 
          ntTMP = nt
        self.mDict[iM].append((nt,duration.convertQuarterLengthToType(ntDur)))
        if debug: print iM, ntDur,duration.convertQuarterLengthToType(ntDur) , mLen
    return

  def Show(self):
    debug=0
    self.part = stream.Part()
    for iM in range(0,len(self.mDict.keys())):
        m = stream.Measure()
        for pitchName, durType in self.mDict[iM]:
            if debug: print pitchName, durType
            n = note.Note(pitchName)
            n.duration.type = durType
            m.append(n)
        self.part.append(m)
    return 



def add(*parts):
  score=stream.Score()
  for p in parts:
    score.insert(0,p)
  return score
  

a = randSong(10,'c')
b = randSong(10,'c')
a.Show()
b.Show()
c=add(a.part,b.part)
c.show()

'''
sCadence = stream.Score()
sCadence.insert(0, partUpper)
sCadence.insert(0, partLower)
sCadence.show()
'''


'''


for iM in range(0,nMeasures):  
  measures[iM]=[]
  
  mLen=0
  while mLen < lenMeasure:
    #ntDur = sample(noteDurs,1)[0]
    ntDur = randwWeight(noteDursWeight)[0]
    
    if mLen + ntDur > lenMeasure:   
      ntDur = lenMeasure - mLen  
      while ntDur not in noteDurs:
        ntDur -= noteDurs[0]
        print 'BEING SUBTRACTED', ntDur

 
    mLen = mLen + ntDur
    #nt= harmony(key,fscale[randint(0,6)])
    nt = harmony(key,randwWeight(fScaleW)[0])
    measures[iM].append((nt,duration.convertQuarterLengthToType(ntDur)))
    print iM, ntDur,duration.convertQuarterLengthToType(ntDur) , mLen 


randSong = stream.Part()

for iM in range(0,nMeasures):
    m = stream.Measure()
    for pitchName, durType in measures[iM]:
        print pitchName, durType
        n = note.Note(pitchName)
        n.duration.type = durType
        m.append(n)
    randSong.append(m)

'''



"""
for iM in range(0,nMeasures):
  mStart = iM*lenMeasure
  mEnd = (iM+1)*lenMeasure
  print mStart , 'to ' , mEnd
  for iN in range(mStart,mEnd):
    print iN
#    print 'note number: ', fscale.index(iN)
    nt = harmony(key,fscale[randint(0,6)])
    music[iM].append((nt,durList[randint(0,2)]))#[iN%len(durList)]))
#    print 'mod is=', fscale.index(iN)%lenMeasure
print music

'''
for iM in range(0,nMeasures):
  print 'Measure = ', iM
  for iN in fscale:
    print fscale.index(iN)
    if fscale.index(iN)%lenMeasure == lenMeasure-1:
      print 'mod is=', fscale.index(iN)%lenMeasure
#      break
    else:
      print 'Note= ', iN
      nt = harmony(key,iN)
      music[iM].append((nt,fnoteDur))
print music
'''


m1 = [('g4', 'quarter'), ('a4', 'quarter'), ('b4', 'quarter'), ('c#5', 'quarter')]
m2 = [('d5', 'whole')]

music1 = [m1,m2]






partUpper = stream.Part()
for mData in music:
  m = stream.Measure()
  for pitchName, durType in mData:
      n = note.Note(pitchName)
      n.duration.type = durType
      m.append(n)
  partUpper.append(m)



'''

partUpper.show()  

sCadence = stream.Score()
sCadence.insert(0, partUpper)
#sCadence.insert(0, partLower)
sCadence.show()

'''
"""
