

import math
import pyaudio
import sys

PyAudio = pyaudio.PyAudio
rate = 16000
wave = 1000

class freq():
  def __init__(self,wave,rate=16000):
    data = ''.join([chr(int(math.sin(x/((rate/wave)/math.pi))*127+128)) for x in xrange(rate)])
    p = PyAudio()

    stream = p.open(format =
                    p.get_format_from_width(1),
                    channels = 1,
                    rate = rate,
                    output = True)
    while True:
        stream.write(data)
    stream.stop_stream()
    stream.close()
    p.terminate()


freq(1000)
print "2nd one"
freq(800)

