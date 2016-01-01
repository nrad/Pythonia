import math,numpy,os
import pygame
import numpy as np
from generate import GenerateTone, Tone, harm
from jup import *
from colordict import colorDict
import matplotlib.pyplot as plt


scale = 40
winx = 1200
winy = 800


c0 = 1100 ## speed of sound
f0 = 440


FPS        =  100
time_scale =  1
clock =  pygame.time.Clock()




moonDict = {
        "Io": {"r":1   ,"p0":(winx/2.,winy/2.)    ,  "color":(99, 195, 14  ,180)    },
        "Ga": {"r":5   ,"p0":(winx/2.,winy/2.)    ,  "color":(20, 82, 142  ,180)    } , 
        "Eu": {"r":2   ,"p0":(winx/2.,winy/2.)    ,  "color":(194, 14, 72  ,180)    },
        "Ca": {"r":7   ,"p0":(winx/2.,winy/2.)    ,  "color":(218, 137, 15 ,180)  },
        #"Ca2": {"r":8  ,"p0":(winx/2.,winy/2.)    , "color":(218, 137, 15 )    ,"color":(189, 112, 0 )},
        }

if __name__=='__main__':

  pygame.init()

  moonDisplay = pygame.display.set_mode( (winx,winy) )
  pygame.display.set_caption("GalieleanMelody")

  moonExit = False

  moons={}
  for moon in moonDict:
    moons[moon]=Moon(moonDict[moon]['r'], p0=moonDict[moon]['p0'], time_scale=time_scale)

  


  #pygame.mixer.init( frequency = freq, size = -bits, channels = len(moons),buffer=512)
  pygame.mixer.init( -16, channels = len(moons),buffer=512)
  chnl={key:pygame.mixer.Channel(i) for i,key in enumerate(moons)}

  arrow,arrow_rect=load_image("arrow")
  arrow=pygame.transform.scale(arrow,(40,2))

  obs='Io'
  def_length=1./24.
  wave = "sine"

  while not moonExit:
    milliseconds = clock.tick(FPS)  # milliseconds passed since last frame
    seconds = milliseconds / 1000.0 # seconds passed since last frame (float)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        moonExit = True
      #print(event)
    
    #moonDisplay.fill((0,0,0))



    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Io'].orbit()[0],moons['Io'].orbit()[1],1 )
    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Eu'].orbit()[0],moons['Eu'].orbit()[1],1 )
    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Ga'].orbit()[0],moons['Ga'].orbit()[1],1 )
    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Ca'].orbit()[0],moons['Ca'].orbit()[1],1 )
      

    
    #pygame.draw.circle(moonDisplay, (100,200,210), sub(moons['Io'].move() , sub(moons['Io'].pos()  ,(winx/2.,winy/2.)  ) ) ,1)
    #pygame.draw.circle(moonDisplay, (100,200,210), sub(moons['Ga'].move() , sub(moons['Io'].pos() ,(winx/2.,winy/2.)  ))   ,1)
    #pygame.draw.circle(moonDisplay, (100,200,210), sub(moons['Eu'].move() , sub(moons['Io'].pos() ,(winx/2.,winy/2.)  ))   ,1)
    #pygame.draw.circle(moonDisplay, (100,200,210), sub(moons['Ca'].move() , sub(moons['Io'].pos() ,(winx/2.,winy/2.)  ))   ,1)

    for moon in moons:
      newPos= transf(moons[moon].move(seconds), moons[obs].pos() )
      #pygame.draw.circle(moonDisplay, moonDict[moon]['color'], sub(moons[moon].move(seconds) , sub(moons[obs].pos() ,(winx/2.,winy/2.)  ))   ,1)
      pygame.draw.circle(moonDisplay, moonDict[moon]['color'], newPos   ,2)

    #print "  ", moons['Io'].pos(), moons['Eu'].pos()
    #print "li", lineToMoon(moons['Io'],moons['Eu']) 
    #pygame.draw.line(moonDisplay, (255,255,255) , *lineToMoon(moons['Io'],moons['Eu']) )


    #pygame.draw.line(moonDisplay, (255,255,255) , moons['Ga'].pos(), moons['Eu'].pos() )
    #pygame.draw.line(moonDisplay, (255,255,255) , moons['Ca'].pos(), moons['Eu'].pos() )


    if False:
      moonList = moons.keys()
      for moon in moons:
        moonList.remove(moon)
        for moon2 in moonList:
          m1Pos = transf(moons[moon].pos(), moons[obs].pos() )
          m2Pos = transf(moons[moon2].pos(), moons[obs].pos() )
          #pygame.draw.line(moonDisplay, (255,255,255) , moons[moon].pos(), moons[moon2].pos() )
          pygame.draw.line(moonDisplay, (255,255,255) , m1Pos, m2Pos )

    #pygame.draw.line(moonDisplay, (255,255,255,10) , transf(moons["Io"].pos(), moons[obs].pos() ), 
    #                                                 transf(moons["Ga"].pos(), moons[obs].pos() ) )      

    
    freq = moons['Io'].distTo(moons["Ga"]) *3
    freq2 = (1+mag(sub(moons['Io'].v, moons["Ga"].v)) / c0 ) * f0
    print freq2
    #print freq
    #s=GenerateTone(freq2,wave=wave,length=seconds)
    s=Tone(func= lambda x: np.sin(x) , freq = freq,length=seconds)
    chnl['Io'].play(s.sound,1)


    #chnl['Ga'].stop()
    #freq = moons['Ga'].distTo(moons['Eu'])
    #print freq
    #s=GenerateTone(freq,wave=wave,length=def_length)
    #chnl['Ga'].play(s,1)


    #chnl['Ca'].stop()
    #freq = moons['Ca'].distTo(moons['Eu'])
    #print freq
    #s=GenerateTone(freq,wave=wave,length=def_length)
    #chnl['Ca'].play(s,1)


    pygame.display.update()
    

    


  pygame.quit()
  #quit()
