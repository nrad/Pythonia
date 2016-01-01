##\example tu_002a_sound_generation.py
#More Advance sound generation!!
#
#\n\n <small>Click on each functions for more detail </small>\n

import peaceaudio
import peaceaudiolib

peaceaudio.init_peaceaudio(sample_rate = 44100, inch = 0, outch=2, framesPerBuffer = 128)
peaceaudio.createTable(1024)
peaceaudio.openStream()


def callback():
	peaceaudio.generate()
	peaceaudio.writeBuffer()
	
track = peaceaudio.createStandTrack(freq=220.0,waveshape=peaceaudio.wavetype.sinewave)
mixer = peaceaudio.createMixer()
mixer.addTrack(track)
track.setvolume(0.5)
peaceaudio.setMixer(mixer)
peaceaudio.setCallback(callback)

peaceaudio.start()
raw_input("Press Enter to exit")
peaceaudio.stop()
