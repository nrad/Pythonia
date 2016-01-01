##\example tu_004b_Realtime_Signal_viewer_customization.py
#Visualization the signal!!
#
#\n\n <small>Click on each functions for more detail </small>\n

import peaceaudio
import peacevisual
import gl
import random 

buffersize = 128
wave = []

peaceaudio.init_peaceaudio_easy(buffersize)
peacevisual.init_peacevisual(800,600)


def callback():
	global wave
	peaceaudio.generate()
	peaceaudio.writeBuffer()
	wave = peaceaudio.getBufferl()#Capture signal from left channel
	return 1
def viewsignal_callback():
	peacevisual.beginDraw(gl.GL_LINES)
	for i in xrange(buffersize):
		peacevisual.setColor4f(random.random(),random.random(),random.random(),0.2)
		peacevisual.drawVertex2f(-0.9,0)
		peacevisual.drawVertex2f(0.9,wave[i])
	peacevisual.endDraw()
	return 1

track = peaceaudio.createStandTrack(waveshape=peaceaudio.wavetype.sinewave)
mixer = peaceaudio.createMixer()
mixer.addTrack(track)
track.setvolume(0.5)
peaceaudio.setMixer(mixer)

peaceaudio.setCallback(callback)
peacevisual.setCallback(viewsignal_callback)



peaceaudio.start()
peacevisual.start()
peacevisual.setLineWidth(10.0)

raw_input("Press Enter to exit")
peaceaudio.stop()


