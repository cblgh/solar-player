import RPi.GPIO as gpio
import subprocess
from time import sleep

SCRIPTS = {"start": "./start.sh", "pause": "./pause.sh", "resume": "./unpause.sh", "loop": "./loop.sh"}

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

# setup the pins to read from
gpio.setmode(gpio.BCM)
gpio.setup(BUTTON1_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(BUTTON2_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(BUTTON3_PIN, gpio.IN, pull_up_down=gpio.PUD_UP)

# add callbacks that will be triggered when a button is pressed (but not when it is released)
# gpio.add_event_detect(BUTTON1_PIN, gpio.RISING)
# gpio.add_event_callback(BUTTON1_PIN, callback)

# start server with a blank video
subprocess.Popen([SCRIPTS["start"], "/home/pi/Videos/empty.m4v"])
current_state = SHOW_EMPTY

while True:
    button_1 = not gpio.input(BUTTON1_PIN)
    button_2 = not gpio.input(BUTTON2_PIN)
    button_3 = not gpio.input(BUTTON3_PIN)

    print "Button 1 input: {}\nButton 2 input: {}\nButton 3 input: {}\n".format(button_1, button_2,
            button_3)

    if button_1 and button_2 and not button_3 and current_state is not LOADING:
        # state 1: loading
        subprocess.Popen([SCRIPTS["loop"], "/home/pi/Videos/loading.mp4"])
        current_state = LOADING
        print "LOADING"
    elif not button_1 and button_2 and button_3 and current_state is not PAUSED:
        # state 4: pause
        subprocess.call([SCRIPTS["pause"]])
        current_state = PAUSED
        print "PAUSE"
    elif not button_1 and button_2 and not button_3 and current_state is not SHOW_MOVIE:
        # state 5: resume
        if current_state == PAUSED:
            subprocess.Popen([SCRIPTS["resume"]])
        else:
            subprocess.Popen([SCRIPTS["loop"], "/home/pi/Videos/video.mp4"])
        print "SHOW MOVIE"
        current_state = SHOW_MOVIE
    elif not button_1 and not button_2 and button_3 and current_state is not SHOW_EMPTY:
        # state 6: show a black screen
        subprocess.Popen([SCRIPTS["loop"], "/home/pi/Videos/empty.m4v"])
        print "SHOW EMPTY SCREEN"
        current_state = SHOW_EMPTY
    elif not button_1 and not button_2 and not button_3 and current_state is not SHOW_SLIDESHOW:
        # state 7: show 3 movies in sequence, todo
        print "SHOW 3 MOVIES IN SEQUENCE"
        current_state = SHOW_SLIDESHOW

    sleep(0.3)
