

notes=('c','d-','d','e-','e','f','g-','g','a-','a','b-','b')

majScale=(0,2,4,5,7,9,11,12)
minScale=(0,2,3,5,7,8,10,12)

intervals={\
	0:'Perfec Unison',
	1:'Minor Second',
	2:'Major Second',
	3:'Minor Third',
	4:'Major third',
	5:'Perfect Fourth',
	6:'6th semitone',
	7:'Perfect Fifth',
	8:'Minor Sixth',
	9:'Major Sixth',
	10:'Minor Seventh',
	11:'Major Seventh',
	12:'PerfectOctave'
	}

durations={\
	'0.25':'quarter',
	'0.5':'half',
	'1.5':'whole'
	}
durList=('16th', 'eighth','quarter','half','whole')

class TwoWayDict(dict):
    def __init__(self,dictionary):
	self.dictionary = dictionary
        for k in self.dictionary.iterkeys():
	    print ditionary[k],
            dict.__setitem__(self, k, dictionary[k])
            dict.__setitem__(self, dictionary[k], k)

    def __setitem__(self):
        # Remove any previous connections with these values
#        if key in self:
#            del self[key]
#        if value in self:
#            del self[value]
	for k in self.dictionary.iterkeys:
            dict.__setitem__(self, self.dictionary[k], self.dictionary[v])
            dict.__setitem__(self, self.dictionary[v], self.dictionary[k])

    def __delitem__(self, key):
        dictionary.__delitem__(self, self[key])
        dictionary.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        return dictionary.__len__(self) // 2






def getAlpha(string):
  for i in string:
    if not i.isalpha(): string = string.replace(i,'')
  return string
def getNum(string):
  for i in string:
    if not i.isdigit(): string = string.replace(i,'')
  return string
def getAcc(string):
  acc = ''
  for i in string:
    if i=='-': 
      acc='-'
      break 
  return acc
def fifth(note):
  if note not in notes: 
    print "Not a note! use a note in:" , notes
  else: 
    fifthIndex = (notes.index(note)+7)%len(notes)
    fif = notes[fifthIndex]
    print fifthIndex
    return fif 

def harmony(fnote,intv):

  if getAcc(fnote)=='-': acc= -1
  else: acc=0

  if not getNum(fnote): fpitch = 4  #default pitch is 4
  else: fpitch = int(getNum(fnote))
  fnote=getAlpha(fnote).lower()
  fpitch += (notes.index(fnote)+intv)//len(notes)
  intv = intv %len(notes) + acc
  #print intv, acc something worng with harmony('d-',0)
  if intv not in intervals.keys():
    print "Interval: ", intv, "Is Not a correct interval, choose an interval in:" , intervals
  else:
#    print str(fpitch)
    noteIndex = (notes.index(fnote)+intv)%len(notes)
    retNote = notes[noteIndex] + str(fpitch)
#    print hNote, 'is the', intervals[intv], ' of ', note
    return retNote




def fib(n,fstart=0):
  fibl=[fstart,fstart+1]
  for i in range(fstart,fstart+n):
    fstart.append(fibl[i]+fib[i+1])
  return fibl
