from generate import GenerateTone
import pygame

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=8)

chnls = [pygame.mixer.Channel(i) for i in xrange(pygame.mixer.get_num_channels() )]
s= GenerateTone(440)

chnls[1].play(s,-1)

