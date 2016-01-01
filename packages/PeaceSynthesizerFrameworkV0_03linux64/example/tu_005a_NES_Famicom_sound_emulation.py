##\example tu_005a_NES_Famicom_sound_emulation.py
#Play sequence data of NES (famicom) sound emulation V0.03
#
#\n\n <small>Click on each functions for more detail </small>\n
#

import peaceaudio
import time
import song.nes.sidepocket_test as demosong

buffersize = 128
peaceaudio.init_peaceaudio(sample_rate = 44100, inch = 0, outch=2, framesPerBuffer = buffersize)
peaceaudio.openStream()

track = peaceaudio.createNESTrack()
track.initStringCompiler(demosong.text)
track.compileString()

def callback():
        peaceaudio.generate()
        peaceaudio.writeBuffer()
        return 1


mixer = peaceaudio.createMixer()
mixer.addTrack(track)

peaceaudio.setMixer(mixer)
peaceaudio.setCallback(callback)
peaceaudio.start()

while track.stringcompiler.alive:
	time.sleep(0.1)
peaceaudio.stop()
print "exit"
