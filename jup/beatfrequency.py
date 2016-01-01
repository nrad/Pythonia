##https://www.reddit.com/r/learnpython/comments/3ctfyf/producing_beat_frequencies_in_pygame/

import pygame
import numpy as np
bits = 16
size = (600,600) 

sample_rate = 44100
duration = 0.1
pygame.mixer.pre_init(sample_rate,-bits, 44100)
pygame.init()
_display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.mixer.set_num_channels(2)
done = False
f1 = 440
n1_samples = int(round(30*sample_rate))
n2_samples = int(round(duration*sample_rate))
max_sample = 2**(bits - 1) - 1
buf1 = np.empty((n1_samples, 2), dtype = np.int16)
buf2 = np.empty((n2_samples, 2), dtype = np.int16)
chan1 = pygame.mixer.Channel(0)
chan2 = pygame.mixer.Channel(1)

def fillWithNumpy(f,buf,phi0):
    samples = len(buf)
    stepSize = 2*np.pi/sample_rate
    buf[:,0] = max_sample*0.5*np.sin(np.arange(samples)*f*stepSize+phi0)
    buf[:,1] = buf[:,0]

def makeSine(f,phi=0,dur=1):
    nSteps = int(round(dur*sample_rate))
    buf = np.empty((nSteps, 2), dtype = np.int16)
    samples = len(buf)
    stepSize = 2*np.pi/sample_rate
    buf[:,0] = max_sample*0.5*np.sin(np.arange(samples)*f*stepSize+phi)
    buf[:,1] = buf[:,0]
    
    finalAmp = nSteps*stepSize*f+phi
    
    return (buf,finalAmp, nSteps*stepSize)

#fillWithNumpy(440,buf1,phi0=0)
#soundbuf1 = pygame.mixer.Sound(buf1)
#chan1.play(soundbuf1,-1)
clk = pygame.time.Clock()
x_prev = 0

   
freq=440
phi=0
while not done:
    #pos = pygame.mouse.get_pos()
    #x = pos[0]
    #y = pos[1]

    #f2 = x - 200.0 + 440.0
    #fillWithNumpy(f2,buf2,phi0=0)
    #soundbuf2 = pygame.mixer.Sound(buf2)
    #chan2.queue(soundbuf2)
    #clk.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_z:
              #fillWithNumpy(freq,buf2,phi0=0)
              #soundbuf2 = pygame.mixer.Sound(buf2)
              buf, finalAmp , finalPos =makeSine(freq,phi=phi,dur=1)
              soundbuf = pygame.mixer.Sound(buf)

              #chan2.queue(soundbuf2)
              chan2.play(soundbuf)
              clk.tick(10)
              print freq
              print finalAmp
              freq+=30
              #phi = finalAmp - freq*finalPos
           

    buf, finalAmp ,finalPos=makeSine(freq,phi=phi,dur=0.3)
    soundbuf = pygame.mixer.Sound(buf)

    #chan2.queue(soundbuf2)
    chan2.play(soundbuf)
    time.sleep(0.4)
    clk.tick(10)
    print freq, finalAmp, finalPos, phi
    freq+=30
    phi = finalAmp - freq*finalPos 
    #phi = 0 
    #phi = finalAmp 

    if freq > 900:
      done =True

pygame.quit()
