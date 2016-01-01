##\example tu_003a_Signal_viewer_basic.py
#View generated signal!!
#
#\n\n <small>Click on each functions for more detail </small>\n

import peaceaudio
import peacevisual
import gl


peaceaudio.init_peaceaudio(framesPerBuffer = 256)#Modify framesPerBuffer for different results
peaceaudio.createTable(1024)
peaceaudio.openStream()
wave = []

def callback():
	peaceaudio.generate()
	peaceaudio.writeBuffer()
	return 1

track = peaceaudio.createStandTrack(freq=220.0,waveshape=peaceaudio.wavetype.sinewave)
mixer = peaceaudio.createMixer()
mixer.addTrack(track)
track.setvolume(0.5)
peaceaudio.setMixer(mixer)

peaceaudio.setCallback(callback)

peaceaudio.start()
raw_input("Press Enter to Continue")
wave = peaceaudio.getBufferl()#Capture signal from left channel


peacevisual.viewsignal(wave)
raw_input("Press Enter to exit")
peaceaudio.stop()

