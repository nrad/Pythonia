import math,numpy,os
import pygame
from generate import GenerateTone

time = 1/1000.
scale = 40
winx = 1200
winy = 800

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def sub(a,b):
  print  [ int(round(a_i - b_i)) for a_i, b_i in zip(a, b)]
  return [ int(round(a_i - b_i)) for a_i, b_i in zip(a, b)]


class Moon():
  def __init__(self,r,phi0=0,p0=(winx/2,winy/2)):
    """ distance in au """
    self.r = r * scale
    self.period = r**(3/2.) /time
    self.dphi   = 2*math.pi / self.period 
    self.speed  = self.dphi* self.r
    self.phi=phi0
    self.x0, self.y0 = p0
    self.x = self.x0 + self.r*math.cos(phi0)
    self.y = self.y0 + self.r*math.sin(phi0)

  def pos(self,type="i"):
    if type.lower() == "i":
      return (int(self.x),int(self.y))
    if type.lower() == "f":
      return (self.x,self.y)
  def orbit(self):
    return ((self.x0, self.y0),int(self.r))

  def move(self):
    self.phi += self.dphi
    #print self.x0 + self.r*math.cos(self.phi)
    self.x = self.x0 + self.r*math.cos(self.phi)
    self.y = self.y0 + self.r*math.sin(self.phi)
    return (int(self.x), int(self.y))

  def angleTo(self,obs):
    assert isinstance(obs,Moon)
    deltaR = (obs.x - self.x, obs.y-self.y)
    return math.atan2(deltaR[1],deltaR[0])*180/math.pi
  
  def distTo(self,moon2):
    (m1x, m1y), (m2x, m2y) = lineToMoon(self,moon2)
    return math.sqrt((m1x-m2x)**2+(m1y-m2y)**2)
  def next():
    pass



def lineToMoon(moon1,moon2,scale=1):
  p2x, p2y = moon2.pos() 
  p1x, p1y = moon1.pos() 
  return moon1.pos(), (p2x*scale, p2y*scale)

class Frequency():
  def __init__(self,freq,duration=1.0,bits=16,channels = 2):
    pygame.mixer.init( frequency = freq, size = -bits, channels = 2,buffer=512)
    self.n_samples = int(round(duration*1000))
    self.buf = numpy.zeros((self.n_samples, 2), dtype = numpy.int16)
    max_sample = 2**(bits - 1) - 1
    for s in range(self.n_samples):
        t = float(s)/freq        # time in seconds
        self.buf[s][0] = int(round(max_sample*math.sin(2*math.pi*440*t)))# left
        self.buf[s][1] = int(round(max_sample*0.5*math.sin(2*math.pi*440*t)))    # right
    self._sound()
  def _sound(self):
    self.sound=pygame.sndarray.make_sound(self.buf)
  def play(self):
    self.sound.play()
  def quit(self):
    pygame.mixer.quit()

if __name__=='__main__':


  pygame.init()

  moonDisplay = pygame.display.set_mode( (winx,winy) )
  pygame.display.set_caption("GalieleanMelody")

  moonExit = False

  moons= {
        "Io": Moon(1),
        "Ga": Moon(4),
        "Eu": Moon(2),
        "Ca": Moon(9.4),
        }

  #pygame.mixer.init( frequency = freq, size = -bits, channels = len(moons),buffer=512)
  pygame.mixer.init( -16, channels = len(moons),buffer=512)
  chnl={key:pygame.mixer.Channel(i) for i,key in enumerate(moons)}

  arrow,arrow_rect=load_image("arrow")
  arrow=pygame.transform.scale(arrow,(40,2))

  obs='Eu'
  def_length=1./24.
  wave = "sine"

  while not moonExit:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        moonExit = True
      #print(event)
    
    moonDisplay.fill((0,0,0))



    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Io'].orbit()[0],moons['Io'].orbit()[1],1 )
    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Eu'].orbit()[0],moons['Eu'].orbit()[1],1 )
    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Ga'].orbit()[0],moons['Ga'].orbit()[1],1 )
    #pygame.draw.circle(moonDisplay, (255,255,255), moons['Ca'].orbit()[0],moons['Ca'].orbit()[1],1 )
      

    
    pygame.draw.circle(moonDisplay, (100,200,210), moons['Io'].move() ,4)
    pygame.draw.circle(moonDisplay, (100,200,210), moons['Ga'].move() ,4)
    pygame.draw.circle(moonDisplay, (100,200,210), moons['Eu'].move() ,4)
    pygame.draw.circle(moonDisplay, (100,200,210), moons['Ca'].move() ,4)



    #print "  ", moons['Io'].pos(), moons['Eu'].pos()
    #print "li", lineToMoon(moons['Io'],moons['Eu']) 
    #pygame.draw.line(moonDisplay, (255,255,255) , *lineToMoon(moons['Io'],moons['Eu']) )


    #pygame.draw.line(moonDisplay, (255,255,255) , moons['Ga'].pos(), moons['Eu'].pos() )
    #pygame.draw.line(moonDisplay, (255,255,255) , moons['Ca'].pos(), moons['Eu'].pos() )


    if True:
      moonList = moons.keys()
      for moon in moons:
        moonList.remove(moon)
        for moon2 in moonList:
          pygame.draw.line(moonDisplay, (255,255,255) , moons[moon].pos(), moons[moon2].pos() )

    
    chnl['Io'].stop()
    freq = moons['Io'].distTo(moons['Eu'])
    print freq
    s=GenerateTone(freq,wave=wave,length=def_length)
    chnl['Io'].play(s,1)


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
