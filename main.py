"""
Entry point of the project.
"""

import player
import person_counter

from sys import platform

if __name__ == '__main__':

    if platform == "darwin":
        port = "/dev/cu.usbmodem14101"
        resolution = (1440, 900)
    else:
        # windows
        port = "COM4"
        resolution = (1440, 900)

    no_arduino = False

    counter = person_counter.PersonCounter(port, no_arduino)
    video_player = player.VideoPlayer(counter, resolution)
