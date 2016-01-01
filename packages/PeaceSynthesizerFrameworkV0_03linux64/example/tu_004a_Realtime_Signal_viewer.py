##\example tu_004a_Realtime_Signal_viewer.py
#Visualization the signal!!
#
#\n\n <small>Click on each functions for more detail </small>\n

import peaceaudio
import peacevisual
import gl

wave = []

peaceaudio.init_peaceaudio_easy(256)
peacevisual.init_peacevisual(800,600)


def callback():
	global wave
	peaceaudio.generate()
	peaceaudio.writeBuffer()
	wave = peaceaudio.getBufferl()#Capture signal from left channel
	return 1
def viewsignal_callback():
	peacevisual.drawsignal(wave)
	return 1

track = peaceaudio.createStandTrack(waveshape=peaceaudio.wavetype.noise)
mixer = peaceaudio.createMixer()
mixer.addTrack(track)
track.setvolume(0.5)
peaceaudio.setMixer(mixer)

peaceaudio.setCallback(callback)
peacevisual.setCallback(viewsignal_callback)


peacevisual.disable(gl.GL_BLEND)
peaceaudio.start()
peacevisual.start()

raw_input("Press Enter to exit")
peaceaudio.stop()

