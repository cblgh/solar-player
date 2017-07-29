import RPi.GPIO as gpio
import subprocess
import os
import time

# mpv scripts to call depending on button I/O, see https://github.com/cblgh/mpv-control for scripts 
MPV_SCRIPTS = {"start": "./start.sh", "pause": "./pause.sh", "resume": "./unpause.sh", "loop": "./loop.sh", "load":
        "./load.sh", "append": "./append.sh"}

# GPIO pins that are used
BUTTON1_PIN = 17
BUTTON2_PIN = 27
BUTTON3_PIN = 22

# internal states
current_state = -1
LOADING = 1
PAUSED = 4
SHOW_MOVIE = 5
SHOW_EMPTY = 6
SHOW_SLIDESHOW = 7

# syntactic sugar
ON = True
OFF = False

# setup the pins to read from
gpio.setmode(gpio.BCM)
gpio.setup(BUTTON1_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(BUTTON2_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(BUTTON3_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)

# add callbacks that will be triggered when a button is pressed (but not when it is released)
# gpio.add_event_detect(BUTTON1_PIN, gpio.RISING)
# gpio.add_event_callback(BUTTON1_PIN, callback)

# start server with a blank video
subprocess.Popen([MPV_SCRIPTS["start"], "/home/pi/Videos/empty.m4v"])
current_state = SHOW_EMPTY
BASE_PATH = "/home/pi/Videos"
SLIDESHOW_PATH = "{}/slideshow".format(BASE_PATH)

# find all movies in the slideshow folder, to be played sequentially (and looped) during state SHOW_SLIDESHOW
slideshow_movies = [f for f in os.listdir(SLIDESHOW_PATH) if os.path.isfile(os.path.join(SLIDESHOW_PATH, f))]

# start looping, checking peridiodically for button inputs
while True:
    button_1 = not gpio.input(BUTTON1_PIN)
    button_2 = not gpio.input(BUTTON2_PIN)
    button_3 = not gpio.input(BUTTON3_PIN)
    buttons = [button_1, button_2, button_3]

    print "Button 1 input: {}\nButton 2 input: {}\nButton 3 input: {}\n".format(button_1, button_2,
            button_3)

    if buttons == [ON, ON, OFF] and current_state is not LOADING:
    # if button_1 and button_2 and not button_3 and current_state is not LOADING:
        # state 1: loading
        subprocess.Popen([MPV_SCRIPTS["loop"], "{}/loading.mp4".format(BASE_PATH)])
        current_state = LOADING
        print "LOADING"
    elif buttons == [OFF, ON, ON] and current_state is not PAUSED:
    # elif not button_1 and button_2 and button_3 and current_state is not PAUSED:
        # state 4: pause
        subprocess.call([MPV_SCRIPTS["pause"]])
        current_state = PAUSED
        print "PAUSE"
    elif buttons == [OFF, ON, OFF] and current_state is not SHOW_MOVIE:
    # elif not button_1 and button_2 and not button_3 and current_state is not SHOW_MOVIE:
        # state 5: resume
        if current_state == PAUSED:
            subprocess.Popen([MPV_SCRIPTS["resume"]])
        else:
            subprocess.Popen([MPV_SCRIPTS["loop"], "{}/video.mp4".format(BASE_PATH)])
        print "SHOW MOVIE"
        current_state = SHOW_MOVIE
    elif buttons == [OFF, OFF, ON] and current_state is not SHOW_EMPTY:
    # elif not button_1 and not button_2 and button_3 and current_state is not SHOW_EMPTY:
        # state 6: show a black screen
        subprocess.Popen([MPV_SCRIPTS["loop"], "{}/empty.m4v".format(BASE_PATH)])
        print "SHOW EMPTY SCREEN"
        current_state = SHOW_EMPTY
    elif buttons == [OFF, OFF, OFF] and current_state is not SHOW_SLIDESHOW:
    # elif not button_1 and not button_2 and not button_3 and current_state is not SHOW_SLIDESHOW:
        # state 7: show 3 movies in sequence
        print "SHOW 3 MOVIES IN SEQUENCE"
        current_state = SHOW_SLIDESHOW
        subprocess.Popen([MPV_SCRIPTS["loop"], "{}/{}".format(BASE_PATH, slideshow_movies[0])])
        for movie in slideshow_movies[1:]:
            print "APPENDING " + movie
            subprocess.Popen([MPV_SCRIPTS["append"], "{}/{}.mp4".format(BASE_PATH, movie)])

    # sleep a bit to avoid taxing the cpu
    time.sleep(.15)
