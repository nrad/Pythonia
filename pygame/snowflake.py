import pygame,random
from pygame.locals import *
import math


winWidth=800



##############
pygame.init()
window = pygame.display.set_mode((winWidth, winWidth))
pygame.display.set_caption("Snowflake")
screen = pygame.display.get_surface()


mag = lambda x: math.sqrt(sum([i**2 for i in x]))



def midpoints(pt1 , pt2):
   (x1, y1) = pt1
   (x2, y2) = pt2
   return ((x1+x2)/2, (y1 + y2)/2)

def midline(pt1, pt2):
  (x1, y1) = pt1
  (x2, y2) = pt2
  return [(x1 + float(x2-x1)/3.0,y1 + float(y2-y1)/3.0), (x1 + float(x2-x1)*2.0/3,y1+ float(y2-y1)*2.0/3)]

class Line(object):
  def __init__(self, start_pos, end_pos, color, width):
    object.__init__(self)
    self.start_pos = start_pos
    self.end_pos = end_pos
    self.color = color
    self.width = width

  def draw():
    pygame.draw.line(screen,self.color,self.start_pos,self.end_pos,self.width)
  def split():
    mag(
    end_pos1
    pygame.draw.line(screen,color,

class line:
  
  def __init__(self,x1,y1,x2,y2):
    pygame.draw.line(screen,(255,255,255), (x1, y1), (x2, y2),2)

  def removeMiddle(self):
    pass    
    
pygame.display.update()   
