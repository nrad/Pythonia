from turtle import *

color('black','blue')
clearscreen()

step_length=50
speed(6)

def left_forward(deg,length,ret=False):
  left(deg)
  forward(length)
  if ret: back(step_length)

def split(deg,length,secondDegMult):
  left_forward(deg,length,True)
  left_forward(deg*secondDegMult,length,False)
  
def roundlist(mylist,roundto=1):
  retlist=[]
  for i in mylist:
    retlist.append(round(i,roundto))
  if type(mylist)==type(()):
    retlist=tuple(retlist)
  return retlist

def areEqual(a,b):
  #if round(a[0],2) == round(b[0],2) and round(a[1],2) == round(b[1],2): 
  if roundlist(a)==roundlist(b):
    return True
  else: return False

 


def draw(secondDegMult,lastMove=False):
  initial_position= pos()
  #print initial_position
  while True:
    split(45,step_length,secondDegMult)
    #print abs(pos())
    if areEqual(pos(),initial_position): 
      #print 'pos:', pos()
      #clear()
      if lastMove:
        left(45)
        forward(50)
      return (round(pos()[0]),round(pos()[1]))
      break



while True:
  speed(50)
  draw(5,True)
  if roundlist(pos(),1) == [0.0,0.0]:
    left(45)
    forward(50)
    right(45)
    forward(50)
    left(90)
    forward(50)
    break
#while True:
  
  
