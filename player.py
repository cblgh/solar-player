import RPi.GPIO as gpio
import subprocess
import os
import time
import os

# the interval by which we check to see if any pins have changed
POLLING_INTERVAL = 0.15

# paths that are used, change BASE_PATH to where your movies will reside
BASE_PATH = "/home/pi/Videos"
# the name of the subfolder of BASE_PATH that will contain your slideshow movies 
# (i.e. 3 movies-in-sequence movies)
SLIDESHOW_PATH = "{}/slideshow".format(BASE_PATH)
# the file formats you want to play from the slideshow directory
FILE_FORMATS = ("mp4", "m4v", "avi", "webm")

# change this from ".", by which is meant the current directory, to the directory of the mpv scripts
MPV_SCRIPT_DIRECTORY = "."
# mpv scripts to call depending on button I/O, see https://github.com/cblgh/mpv-control for scripts 
MPV_SCRIPTS = {"start": "start.sh", "pause": "pause.sh", "resume": "unpause.sh", "loop": "loop.sh", "load":
        "load.sh", "append": "append.sh"}
# prefix script names with script path
for key, script in MPV_SCRIPTS.viewitems():
    # os.path.expanduser expands relative directories such as ~/dir to /home/pi/dir
    MPV_SCRIPTS[key] = os.path.expanduser(os.path.join(MPV_SCRIPT_DIRECTORY, script))


# GPIO pins that are used
BUTTON1_PIN = 17
BUTTON2_PIN = 27
BUTTON3_PIN = 22

# internal states
current_state = -1
# the integer values of the states correspond to the states from the manual's state graph
LOADING = 1
PAUSED = 4
SHOW_MOVIE = 5
SHOW_EMPTY = 6
SHOW_SLIDESHOW = 7

# syntactic sugar
ON = True
OFF = False

# setup the pins we read from
gpio.setmode(gpio.BCM)
gpio.setup(BUTTON1_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(BUTTON2_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(BUTTON3_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)

# add callbacks that will be triggered when a button is pressed (but not when it is released)
# NOTE: ended up not choosing to use callbacks due to ambiguity when triggered, in combination with not working that
# great with multiple buttons
# gpio.add_event_detect(BUTTON1_PIN, gpio.RISING)
# gpio.add_event_callback(BUTTON1_PIN, callback)

# start server with a looping blank video
subprocess.Popen([MPV_SCRIPTS["start"], "{}/empty.m4v".format(BASE_PATH)])
current_state = SHOW_EMPTY

# find all movies in the slideshow folder (which will be played sequentially and looped during state SHOW_SLIDESHOW)
slideshow_movies = [f for f in os.listdir(SLIDESHOW_PATH) if os.path.isfile(os.path.join(SLIDESHOW_PATH, f)) and f.endswith(FILE_FORMATS)]

# start looping, checking peridiodically for button inputs
while True:
    # gpio.PUD_UP gives a 1 when not pressed, and 0 when pressed. thus we invert the input values with 'not' to ensure
    # correct truthiness values for the if clauses below
    button_1 = not gpio.input(BUTTON1_PIN)
    button_2 = not gpio.input(BUTTON2_PIN)
    button_3 = not gpio.input(BUTTON3_PIN)
    buttons = [button_1, button_2, button_3]

    print "Button 1 input: {}\nButton 2 input: {}\nButton 3 input: {}\n".format(*buttons)

    if buttons == [ON, ON, OFF] and current_state is not LOADING:
        # state 1: loading
        print "LOADING"
        subprocess.Popen([MPV_SCRIPTS["loop"], "{}/loading.mp4".format(BASE_PATH)])
        current_state = LOADING
    elif buttons == [OFF, ON, ON] and current_state is not PAUSED:
        # state 4: pause
        print "PAUSE"
        subprocess.call([MPV_SCRIPTS["pause"]])
        current_state = PAUSED
    elif buttons == [OFF, ON, OFF] and current_state is not SHOW_MOVIE:
        # state 5: resume
        print "SHOW MOVIE"
        if current_state == PAUSED:
            subprocess.Popen([MPV_SCRIPTS["resume"]])
        else:
            subprocess.Popen([MPV_SCRIPTS["loop"], "{}/video.mp4".format(BASE_PATH)])
        current_state = SHOW_MOVIE
    elif buttons == [OFF, OFF, ON] and current_state is not SHOW_EMPTY:
        # state 6: show a black screen
        print "SHOW EMPTY SCREEN"
        subprocess.Popen([MPV_SCRIPTS["loop"], "{}/empty.m4v".format(BASE_PATH)])
        current_state = SHOW_EMPTY
    elif buttons == [OFF, OFF, OFF] and current_state is not SHOW_SLIDESHOW:
        print "SHOW 3 MOVIES IN SEQUENCE" # really, though, this method allows for any number of movies in sequence
        # start playing the first movie
        subprocess.Popen([MPV_SCRIPTS["loop"], "{}/{}".format(SLIDESHOW_PATH, slideshow_movies[0])])
        # then append the rest of the movies to the playlist
        for movie in slideshow_movies[1:]:
            print "APPENDING " + movie
            subprocess.Popen([MPV_SCRIPTS["append"], "{}/{}".format(SLIDESHOW_PATH, movie)])
        current_state = SHOW_SLIDESHOW

    # sleep a bit to avoid taxing the cpu
    time.sleep(POLLING_INTERVAL)
