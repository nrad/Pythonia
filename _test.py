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



notewithpitch='{0}{1}'.format(notes[0],4)
fscale = majScale

nMeasures = 2
lenMeasure = 4
nNotes =len(fscale)
key = 'c'

music=[]
fnoteDur = durations['0.25']

measDur = randint(0,len(durations))

for iM in range(0,nMeasures):   music.append([])

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

