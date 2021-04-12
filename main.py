"""
Entry point of the project.
"""

import player
import person_counter


if __name__ == '__main__':
    counter = person_counter.PersonCounter()
    video_player = player.VideoPlayer(counter)

