
import pygame, numpy, math

duration = 1.0          # in seconds
sample_rate = 44100
bits = 16

try:
    pygame.mixer.init(frequency = sample_rate, size = -bits, channels = 2)
    n_samples = int(round(duration*sample_rate))
    buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
    max_sample = 2**(bits - 1) - 1
    for s in range(n_samples):
        t = float(s)/sample_rate        # time in seconds
        buf[s][0] = int(round(max_sample*math.sin(2*math.pi*440*t)))
     # left
        buf[s][1] = int(round(max_sample*0.5*math.sin(2*math.pi*440*t)))    # right
    sound = pygame.sndarray.make_sound(buf)
    sound.play()
    pygame.time.wait(int(round(1000*duration)))

finally:
    pygame.mixer.quit()
