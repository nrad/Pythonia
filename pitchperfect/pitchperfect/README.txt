pitch-perfect, v0.2b
written by Sean McKean

Description:
    This program is meant to demonstrate how to generate audio tones
    without pre-loading them as .wav files. I was thinking about
    including something similar to this method in an upcoming game, to
    make the control a little more interesting. But I do not have a
    date set on it yet, and I still have some bugs to work out.


The Windows binary version can be run without external dependencies;
simply run 'pitch perfect.exe' in the main directory to start the program.

The source version requires the Python interpreter and a couple of libraries
installed:

    Python >= v2.6.6, < v3.0  (http://www.python.org/)
    Pygame >= v1.9.1          (http://www.pygame.org/)
    numpy  >= v1.3.0          (http://numpy.scipy.org/)

To run the program from source, simply call "python main.py" from
the command-line, or "./main.py" if you are on a Unix and have
appropriate permissions set.

Tone generator function:

    To create a dynamic pygame.mixer.Sound with a frequency in mind,
    take a look at the GenerateTone function in generate.py;
    pygame.mixer must be initialized before calling the function.

    For instance:

        import pygame
        from generate import GenerateTone
        ...

        pygame.mixer.init()
        # Creates a 440 Hz A tone sine wave at full volume.
        sound_a = GenerateTone(440.0)
        sound_a.play(-1)
        sound_b = GenerateTone('D#', vol=0.1, wave='square')
        sound_b.play(-1)
        ...


Controls:

    There are some command-line options that can be set, in case you do
    not want to make changes to the program source. Add a "-h" option to
    the program invocation to see a list of the options available.

    This program is mainly mouse-driven, but includes or duplicates some
    keyboard commands as well. To quit, press Escape key or close the
    window. After the program starts, the screen displays a disk with
    lines, and some note names around the perimeter. To select a note,
    left-click the mouse on one of the lines on the disk. To alter the
    volume, click or drag the mouse closer to the center (quieter), or
    closer to the edge (louder). Dragging the mouse through the disk
    with the left button pressed alters the sound in real time, while
    letting go silences the tone. To select a different type of tone for
    playback, click on one of the four buttons displayed in the
    upper-right corner of the window, or press a number key (1-4).
    The fourth waveform (the question mark) is the same as the
    previously selected tone, but it also modulates the frequency
    randomly on playback.

    Chording commands:
        Control keys:   Create a persistent note in current voice and octave.
        Shift keys:     Select a note to alter with left mouse button.
        'c' key:        Cancel selection.
        'x' key:        Delete selected note.
        's' key:        Silence all notes on screen.

    Other commands:
        Right mouse button:             Toggle between-note or on-note modes.
        Middle button scroll:           Alter current octave by a third in
                                        either direction.
        Left and right arrow keys:      (same as above)
        Middle button down and scroll:  Raise or lower current octave by
                                        a full count.
        Up and down arrow keys:         (same as above)
        Middle mouse button, no scroll: Reset current octave, keeping
                                        the current third.
        Space key:                      (same as above)
        'd' key:                        Show some debugging information.

Changelog:

    v0.2b (2010-11-07): Added note chording and abstracted the tone
                        generation function to a separate module.

    v0.1b (2010-11-05): Initial release.


Credits:

    Due credit goes to David Cole for suggesting the ability to add and
    alter chords, and to Jug for the idea of separating the tone
    generator function for independent use.


Please let me know what you think of this program, or if you have
encountered a bug or have a fix. The current version crashes with a
segmentation fault sometimes, but I am having difficulty faithfully
reproducing the bug. All feedback is welcome.

Email: <smckean83 AT gmail DOT com>
