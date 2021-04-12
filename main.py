"""
Entry point of the project.
"""

import player
import person_counter


if __name__ == '__main__':

    port = "/dev/cu.usbmodem14201"
    counter = person_counter.PersonCounter(port)
    video_player = player.VideoPlayer(counter)

