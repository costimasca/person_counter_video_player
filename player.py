import time

import cv2
import vlc

import person_counter


class VideoPlayer:
    """
    Plays one of 5 videos, depending on how many people are detected by the person counter instance.
    Handles the flash during a transition.
    Also plays the sound in sync with the videos.
    """
    def __init__(self, counter: person_counter.PersonCounter, resolution):
        self.counter = counter
        self._current_video = cv2.VideoCapture(self.get_video_from_number(counter.people_count))
        # duration between 2 consecutive frames
        self.delta_time = 1/self._current_video.get(cv2.CAP_PROP_FPS)
        self.video_request_number = None

        self.previous_time = 0
        self.current_time = 0

        self.current_frame = 0
        self.relative_time = 0

        self.transition_flash = False
        self.flash_value = -1

        # sound
        self.media_player = vlc.MediaPlayer(self.get_sound_from_number(counter.people_count))
        self.media_player.play()
        self.new_song = None

        cv2.namedWindow("window", cv2.WINDOW_FREERATIO)
        cv2.setWindowProperty("window", cv2.WND_PROP_OPENGL, cv2.WINDOW_OPENGL)
        self.resolution = resolution

        self.run()

    def run(self):
        """
        Main function of the player. Also does the transition to another video if it has to.
        :return:
        """

        while True:
            if self.counter.number_changed:
                self.transition()

            frame = self.get_current_frame()
            self.overlay_people_count(frame)
            frame = cv2.resize(frame, self.resolution, interpolation=cv2.INTER_CUBIC)
            cv2.imshow("window", frame)

            self.wait_for_fps()

    def wait_for_fps(self):
        """
        Wait the appropriate amount of time to have a fixed fps. delta_time is precomputed and is the duration
        between two frames.

        Also passes any key that is pressed to the key event handler.
        :return:
        """
        while True:
            self.current_time = time.perf_counter()
            if self.current_time - self.previous_time > self.delta_time:
                self.previous_time = self.current_time
                break
            pressed_key = cv2.waitKeyEx(1)
            self.counter.key(pressed_key)

    def get_current_frame(self):
        """
        Returns the frame that should be displayed next. Handles restarting the video from scratch if it has reached
        the end. Also adds the flash to the frame if a transition is in effect.
        :return:
        """
        ret, frame = self._current_video.read()
        if not ret:
            # if end of video reached, start again from the current video
            self._current_video = cv2.VideoCapture(self.get_video_from_number(self.counter.people_count))
            self.current_frame = 0
            ret, frame = self._current_video.read()
            if not ret:
                exit("Cannot start video from the beginning")

            # handle sound
            self.media_player.stop()
            self.media_player.release()
            self.media_player = vlc.MediaPlayer(self.get_sound_from_number(self.counter.people_count))

        if self.transition_flash:
            frame = self.flash(frame)

        self.current_frame += 1

        return frame

    def overlay_people_count(self, image):
        """
        Writes the number of people on the image before showing it.
        :param image:
        :return:
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, str(self.counter.people_count), (10, 550), font, 1, (232, 167, 152), 2, cv2.LINE_AA)

    def transition(self):
        """
        Performs a smooth transition of the video and the sound to the video identified by self.video_request_number.
        Sets the video_request_number back to None when finished
        :return:
        """
        print("Transitioning now")
        # must set to false after handling the transition
        self.counter.number_changed = False
        self._current_video.release()

        self._current_video = cv2.VideoCapture(self.get_video_from_number(self.counter.people_count))
        self._current_video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        # set to true so that the flash can be done
        self.transition_flash = True

    def fade_sound(self):
        """

        :return:
        """
        if 0.5 <= self.flash_value <= 1:
            self.media_player.audio_set_volume(int(100 * self.flash_value))

        elif self.flash_value < 0.5:
            self.media_player.stop()

    def flash(self, img):
        """Handles the image distortion applied to multiple frames that form the flash during a transition between
        two videos.
        """
        def compute_flash(im):
            v2 = 2 - self.flash_value

            im = im * v2 + (1 - v2) * 255

            return im

        def compute_sound_time():
            return int(self.current_frame * self.delta_time * 1000)

        if self.flash_value == -1:
            if self.transition_flash:
                print("Starting flash")
                self.flash_value = 1

                # sound handling
                self.new_song = vlc.MediaPlayer(self.get_sound_from_number(self.counter.people_count))
                t = compute_sound_time()
                print("time:" + str(t))
                self.new_song.audio_set_volume(0)
                self.new_song.play()
                self.new_song.set_time(t)

                return compute_flash(img)

        elif self.flash_value <= 0:
            print("Flash finished")
            self.flash_value = -1
            self.transition_flash = False

            # handle sound
            self.media_player.stop()
            self.media_player.release()
            self.media_player = self.new_song

            return img

        elif self.flash_value > 0:
            self.flash_value -= 0.05

            # handle sound
            self.media_player.audio_set_volume(int(100 * self.flash_value))
            self.new_song.audio_set_volume(int(100 * (1 - self.flash_value)))

            return compute_flash(img)

    @staticmethod
    def get_video_from_number(number):
        """
        Returns the path to the video identified by it's number
        :param number: between 0 and 5
        :return:
        """

        base_path = "videos/Compozitie mare "
        if not 0 <= number <= 5:
            exit("no video with number: " + number)

        else:
            return base_path + "{}.avi".format(number)

    @staticmethod
    def get_sound_from_number(number):
        """
        Returns the path to the sound file identified by it's number
        :param number: between 0 and 5
        :return:
        """

        base_path = "sounds/sound "
        if not 0 <= number <= 5:
            exit("no sound file with number: " + number)

        else:
            return base_path + "{}.mp4".format(number)
