# solar-player
a python script for controlling an [mpv](https://mpv.io/) player using [GPIO](https://pinout.xyz/) inputs.  
Intended to be used in combination with [mpv-control](https://github.com/cblgh/mpv-control).

### Usage
```py
python2 player.py
```

### Script Variables
There are some script variables that might be good to change, depending on your usecase.

```py
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
```

### Assumptions
This was made to be used for an installation which had certain needs. Fundamentally there are four different states the player can be in.  
1. Showing a blank screen
   * This is done through looping a blank video file with name `empty.m4v` located in `BASE_PATH`.
1. Showing a loading video
   * This is done through looping a video file with name `loading.mp4` located in `BASE_PATH`.
1. Playing the main video
   * This is done through looping a video file with name `video.mp4` located in `BASE_PATH`.
1. Slideshow mode, showing a sequence of movies one after the other
   * The sequence of movies is found in the path `{BASE_PATH}/slideshow`. 
  The names don't matter, and neither does the number of files. They do however have to end with one of the formats found in `FILE_FORMATS` above.
### Showing a blank scree

### Startup script
To start the script automatically on a Raspberry Pi Zero with Raspbian installed I added the following to `/etc/rc.local`

```sh
# Execute python media server
sleep 20s && cd /home/pi/mpv-control/ && sudo -H -u pi /usr/bin/python2.7 /home/pi/mpv-control/player.py &
```

* The sleep is probably not necessary, but is rather to give the Raspberry some time to startup.
* We move to the home directory in the event that the script variable `MPV_SCRIPTS_DIRECTORY` hasn't been changed from `"."`
* We preface running the script with `sudo -H -u pi` to change to the default user, as the script is otherwise run as root. 
It works when run as root, but for some reason the screen resolution isn't forced to fullscreen, which it (correctly) is when run as the default user.
* `/usr/bin/python2.7 /home/pi/mpv-control/player.py &` run the script using python2.7, and run it in the background. (As it is a forever loop, the raspberry won't continue booting if `&` is forgotten.)
