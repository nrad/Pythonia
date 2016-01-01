import sys
import os
import pygame as pg
import numpy as np
import math
np.erf = np.frompyfunc(math.erf,1,1)


__all__ = [ 'GenerateTone' ]


notes_dct = {
        'a': 0.0, 'a#': 1.0, 'bb': 1.0, 'b': 2.0, 'c': 3.0, 'c#': 4.0,
        'db': 4.0, 'd': 5.0, 'd#': 6.0, 'eb': 6.0, 'e': 7.0, 'f': 8.0,
        'f#': 9.0, 'gb': 9.0, 'g': 10.0, 'g#': 11.0, 'ab': 11.0,
        }
def_length = 1.0 / 24.0
log440 = np.log2(440.0)


def GenerateTone( freq=440.0,phase=0, vol=1.0, wave='sine', random=False,
                  length=def_length ):
    """ GenerateTone( freq=440.0, vol=1.0, wave='sine', random=False,
                      length=(1.0 / 24.0) ) -> pygame.mixer.Sound

        freq:  frequency in Hz; can be passed in as an int, float,
               or string (with optional trailing octave, defaulting to 4):
               'A4' (440 Hz), 'B#', 'Gb-1'
        vol:  relative volume of returned sound; will be clipped
              into range 0.0 -> 1.0
        wave:  int designating waveform returned;
               one of 'sine', 'saw', or 'square'
        random:  boolean value; if True will modulate frequency randomly
        length:  relative length of the Sound returned;
                 bigger values will result in more longer and more accurate
                 waveforms, but will also take longer to create;
                 the default value should be adequate for most uses
    """

    (pb_freq, pb_bits, pb_chns) = pg.mixer.get_init()
    multiplier = int(freq * length)
    length = max(1, int(float(pb_freq) / freq * multiplier))
    lin = np.linspace(0.0, multiplier, length, endpoint=False)
    if wave == 'sine':
        ary = np.sin(lin * 2.0 * np.pi)
    elif wave == 'saw':
        ary = 2.0 * ((lin + 0.5) % 1.0) - 1.0
    elif wave == 'square':
        ary = np.zeros(length)
        ary[lin % 1.0 < 0.5] = 1.0
        ary[lin % 1.0 >= 0.5] = -1.0
    else:
        print "wave parameter should be one of 'sine', 'saw', or 'square'."
        return None

    # If mixer is in stereo mode, double up the array information for
    # each channel.
    if pb_chns == 2:
        ary = np.repeat(ary[..., np.newaxis], 2, axis=1)

    if pb_bits == 8:
        snd_ary = ary * vol * 127.0
        return pg.sndarray.make_sound(snd_ary.astype(np.uint8) + 128)
    elif pb_bits == -16:
        snd_ary = ary * vol * float((1 << 15) - 1)
        return pg.sndarray.make_sound(snd_ary.astype(np.int16))
    else:
        print "Sound playback resolution unsupported (either 8 or -16)."
        return None


def harm ( a1=1,a2=0.7,a3=0.2,a4=0.15,a5=0.1,a6=0.05,a7=0.001,a8=0.05, b2=0.3,b3=0.2,b4=0.1,b5=0.1 ):
  higher_overtones = lambda freq: a1*np.sin(freq) + a2*np.sin(freq*2) + a3*np.sin(freq*3) + a4*np.sin(freq*4) + a5*np.sin(freq * 5) + a6*np.sin(freq*6) + a7*np.sin(freq*7) + a8*np.sin(freq*8)
  lower_overtones = lambda freq: b2*np.sin(freq/2.) + b3*np.sin(freq/3.) + b4*np.sin(freq/4.)  + b5* np.sin(freq/5.)

  return lambda freq: higher_overtones(freq) + lower_overtones(freq)

class Tone():

  def __init__(self, func = lambda x:  np.sin(x ) ,freq=440  , vol=1.0,  random=False,
                  length=def_length ):

    (pb_freq, pb_bits, pb_chns) = pg.mixer.get_init()
  
    self.freq=freq  

    self.multiplier  = int(freq * length)
    #self.multiplier = freq * length
    self.length = max(1, int(float(pb_freq) / freq * self.multiplier))
    self.lin    = np.linspace(0.0, self.multiplier, self.length, endpoint=False)
    #self.lin2 = np.linspace(0.0,m


    #self.lin = np.linspace(0.0, )



    #self.ary = np.sin(self.lin * 2.0 * np.pi)
    self.ary = func(self.lin*2*np.pi)

    fade_fac=1.
    fadeout_len = min(50, int(len(self.lin)*0.01 ))
    self.fadein= np.arctan(self.lin/fade_fac)/(np.pi/2.)

    #self.fadeout= (1. + np.arctan(- ( self.lin - self.lin[-fadeout_len])/fade_fac )/(np.pi/2.))
    self.fadein  =  np.erf( self.lin  )
    self.fadeout =  0.5 - np.erf(self.lin- self.lin[-50]).astype('f2')/2.
    self.fadeinout = np.multiply(self.fadein, self.fadeout)
    self.ary = np.multiply(self.fadeinout,self.ary)


    norm = abs(1./self.ary.max())
    self.ary = self.ary* norm
    norm2 = abs(1./self.ary.min())
    self.ary = self.ary*norm2

    # If mixer is in stereo mode, double up the array information for
    # each channel.
    if pb_chns == 2:
        self.ary2 = np.repeat(self.ary[..., np.newaxis], 2, axis=1)
    else:
        self.ary2 = self.ary
    if pb_bits == 8:
        snd_ary = self.ary2 * vol * 127.0
        self.sound= pg.sndarray.make_sound(snd_ary.astype(np.uint8) + 128)
    elif pb_bits == -16:
        snd_ary = self.ary2 * vol * float((1 << 15) - 1)
        self.sound= pg.sndarray.make_sound(snd_ary.astype(np.int16))
    else:
        print "Sound playback resolution unsupported (either 8 or -16)."
        return None

if __name__ == '__main__':
  pg.init();
  pg.mixer.init(frequency= 44100, size= -16, channels = 2 ,buffer= 65536 );
  s=GenerateTone(120,0,length=10)
  #s.play()

  import matplotlib.pyplot as plt
  z=Tone(lambda x: np.sin(x * 2.0*np.pi) - 1/2* np.sin(x * np.pi) + 3* np.sin( x* np.pi/3. + 2) )
  zp=plt.plot(z.lin,z.ary)
  #plt.show()
