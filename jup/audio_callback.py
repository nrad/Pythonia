import pyaudio
import wave
import time
import sys
import math
#if len(sys.argv) < 2:
#    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
#    sys.exit(-1)
#
#wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()


rate = 16000
wave = 1000


# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data = ''.join([chr(int(math.sin(x/((rate/wave)/math.pi))*127+128)) for x in xrange(rate)])
    #data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(1),
                channels=2,
                rate=rate,
                output=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
#while stream.is_active():
#    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()
