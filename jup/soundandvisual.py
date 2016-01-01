import pygame
from pygame.locals import *
import math
import numpy

#----------------------------------------------------------------------
# functions
#----------------------------------------------------------------------

def SineWave(freq=1000, volume=16000, length=1):

    num_steps = length * SAMPLE_RATE
    s = []

    for n in range(num_steps):
        value = int(math.sin(n * freq * (6.28318/SAMPLE_RATE) * length) * volume)
        s.append( [value, value] )

    return numpy.array(s)

#-------------------

def SquareWave(freq=1000, volume=100000, length=1):

    num_steps = length * SAMPLE_RATE
    s = []

    length_of_plateau = int( SAMPLE_RATE / (2*freq) )

    print num_steps, length_of_plateau

    counter = 0
    state = 1

    for n in range(num_steps):

        value = state * volume

        s.append( [value, value] )

        counter += 1

        if counter == length_of_plateau:
            counter = 0
            state *= -1

    return numpy.array(s)

#-------------------

def MakeSound(arr):
    return pygame.sndarray.make_sound(arr)

#-------------------

def MakeSquareWave(freq=1000):
    return MakeSound(SquareWave(freq))

#-------------------

def MakeSineWave(freq=1000):
    return MakeSound(SineWave(freq))

#-------------------

def DrawSineWave():

    # sine wave

    yPos = -1 * math.sin(step) * AMPLITUDE
    posRecord['sin'].append((int(xPos), int(yPos) + WIN_CENTERY))
    if showSine:
        # draw the sine ball and label
        pygame.draw.circle(screen, RED, (int(xPos), int(yPos) + WIN_CENTERY), 10)
        sinLabelRect.center = (int(xPos), int(yPos) + WIN_CENTERY + 20)
        screen.blit(sinLabelSurf, sinLabelRect)

    # draw the waves from the previously recorded ball positions
    if showSine:
        for x, y in posRecord['sin']:
            pygame.draw.circle(screen, DARKRED, (x, y), 4)


#-------------------

def DrawSquareWave():

    # square wave

    posRecord['square'].append((int(xPos), int(yPosSquare) + WIN_CENTERY))
    if showSquare:
        # draw the square ball and label
        pygame.draw.circle(screen, GREEN, (int(xPos), int(yPosSquare) + WIN_CENTERY), 10)
        squareLabelRect.center = (int(xPos), int(yPosSquare) + WIN_CENTERY + 20)
        screen.blit(squareLabelSurf, squareLabelRect)

    # draw the waves from the previously recorded ball positions
    if showSquare:
        for x, y in posRecord['square']:
            pygame.draw.circle(screen, BLUE, (x, y), 4)

#----------------------------------------------------------------------
# constants - (uppercase name)
#----------------------------------------------------------------------

# set up a bunch of constants
WHITE      = (255, 255, 255)
DARKRED    = (128,   0,   0)
RED        = (255,   0,   0)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 255,   0)
BLUE       = (  0,   0, 255)

BGCOLOR = WHITE

WINDOWWIDTH = 1200 # width of the program's window, in pixels
WINDOWHEIGHT = 720 # height in pixels

WIN_CENTERX = int(WINDOWWIDTH / 2) # the midpoint for the width of the window
WIN_CENTERY = int(WINDOWHEIGHT / 2) # the midpoint for the height of the window

FPS = 160 # frames per second to run at

AMPLITUDE = 80 # how many pixels tall the waves with rise/fall.

#-------------------

SAMPLE_RATE = 22050 ## This many array entries == 1 second of sound.

SINE_WAVE_TYPE = 'Sine'
SQUARE_WAVE_TYPE = 'Square'

#----------------------------------------------------------------------
# main program
#----------------------------------------------------------------------

#-------------------
# variables (which don't depend on pygame)
#-------------------

sound_types = {SINE_WAVE_TYPE:SQUARE_WAVE_TYPE, SQUARE_WAVE_TYPE:SINE_WAVE_TYPE}

current_type = SINE_WAVE_TYPE
current_played = { 'z': None, 'c': None }
current_drawn = None

#-------------------

# variables that track visibility modes
showSine = True
showSquare = True

xPos = 0
step = 0 # the current input f

posRecord = {'sin': [], 'square': []} # keeps track of the ball positions for drawing the waves

yPosSquare = AMPLITUDE # starting position

#-------------------
# start program
#-------------------

pygame.init()

screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Nibbles!')

# making text Surface and Rect objects for various labels

pygame.display.set_caption('Trig Waves')
fontObj = pygame.font.Font('freesansbold.ttf', 16)

### HERE 
squareLabelSurf = fontObj.render('square', True, BLUE, BGCOLOR)
squareLabelRect = squareLabelSurf.get_rect()

sinLabelSurf = fontObj.render('sine', True, RED, BGCOLOR)
sinLabelRect = sinLabelSurf.get_rect()

#-------------------
# mainloop
#-------------------

fps_clock = pygame.time.Clock()

_running = True

while _running:

    #-------------------
    # events
    #-------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            _running = False

        # some keys don't depend on `current_type`

        elif event.type == KEYDOWN:

            if event.key == K_ESCAPE:
                _running = False

            if event.key == K_RETURN:
                current_type = sound_types[current_type]  #Toggle
                print 'new type:', current_type

        # some keys depend on `current_type`

        if current_type == SINE_WAVE_TYPE:

            if event.type == KEYDOWN:

                #lower notes DOWN

                if event.key == K_z:
                    print current_type, 130.81
                    current_played['z'] = MakeSineWave(130.81)
                    current_played['z'].play()
                    current_drawn = DrawSineWave

                elif event.key == K_c:
                    print current_type, 180.81
                    current_played['c'] = MakeSineWave(180.81)
                    current_played['c'].play()
                    current_drawn = DrawSineWave

            elif event.type == KEYUP:

                #lower notes UP

                if event.key == K_z:
                    current_played['z'].fadeout(350)
                    current_drawn = None

                    #sine - reset data
                    xPos = 0
                    posRecord['sin'] = []
                    step = 0

                elif event.key == K_c:
                    current_played['c'].fadeout(350)
                    current_drawn = None

                    #sine - reset data
                    xPos = 0
                    posRecord['sin'] = []
                    step = 0

        elif current_type == SQUARE_WAVE_TYPE:

            if event.type == KEYDOWN:

                #lower notes DOWN

                if event.key == K_z:
                    print current_type, 130.81
                    current_played['z'] = MakeSquareWave(130.81)
                    current_played['z'].play()
                    current_drawn = DrawSquareWave

                elif event.key == K_c:
                    print current_type, 180.81
                    current_played['c'] = MakeSquareWave(180.81)
                    current_played['c'].play()
                    current_drawn = DrawSquareWave

            elif event.type == KEYUP:

                #lower notes UP

                if event.key == K_z:
                    current_played['z'].fadeout(350)
                    current_drawn = None

                    # square - reset data
                    xPos = 0
                    yPosSquare = AMPLITUDE
                    posRecord['square'] = []
                    step = 0

                elif event.key == K_c:
                    current_played['c'].fadeout(350)
                    current_drawn = None

                    # square - reset data
                    xPos = 0
                    yPosSquare = AMPLITUDE
                    posRecord['square'] = []
                    step = 0

    #-------------------
    # draws
    #-------------------

    # fill the screen to draw from a blank state
    screen.fill(BGCOLOR)

    if current_drawn:
        current_drawn()

    pygame.display.update()

    #-------------------
    # moves
    #-------------------

    if current_drawn:
        xPos += 1.0 #0.5

        if xPos > WINDOWWIDTH:
            #sine ### HERE
            xPos = 0
            posRecord['sin'] = []
            step = 0

            # square ### HERE
            yPosSquare = AMPLITUDE
            posRecord['square'] = []
        else:
            #sine ### HERE


            # square ### HERE
            # jump top and bottom every 100 pixels
            if xPos % 100 == 0:
                yPosSquare *= -1
                # add vertical line
                for x in range(-AMPLITUDE, AMPLITUDE):
                    posRecord['square'].append((int(xPos), int(x) + WIN_CENTERY))

    #-------------------
    # FPS
    #-------------------

    fps_clock.tick(FPS)

#-------------------
# end program
#-------------------

pygame.quit()
