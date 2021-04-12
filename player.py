import time

import cv2
import vlc

import person_counter


class VideoPlayer:
    def __init__(self, counter: person_counter.PersonCounter):
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

        self.run()

    def run(self):
        """
        Main function of the player. Keeps track of the current frame and time and plays the video. Also does the
        transition to another video if it has to.
        :return:
        """
        # song = vlc.MediaPlayer('song.mp3')
        # song.play()
        # song.set_time(10000)

        while True:
            if self.counter.number_changed:
                self.transition()

            frame = self.get_current_frame()
            self.overlay_people_count(frame)
            cv2.imshow("window", frame)

            # wait the appropriate amount of time to have a fixed fps
            while True:
                self.current_time = time.perf_counter()
                if self.current_time - self.previous_time > self.delta_time:
                    self.previous_time = self.current_time
                    break
                pressed_key = cv2.waitKey(1)
                self.counter.key(pressed_key)

    def get_current_frame(self):
        ret, frame = self._current_video.read()
        if not ret:
            # if end of video reached, start again from the current video
            self._current_video = cv2.VideoCapture(self.get_video_from_number(self.counter.people_count))
            self.current_frame = 0
            ret, frame = self._current_video.read()
            if not ret:
                exit("Cannot start video from the beginning")

        if self.transition_flash:
            frame = self.flash(frame)

        self.current_frame += 1

        return frame

    def overlay_people_count(self, image):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, str(self.counter.people_count), (10, 550), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

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

    def flash(self, img):

        def compute_flash(im):
            v2 = 2 - self.flash_value

            im = im * v2 + (1 - v2) * 255

            return im

        if self.flash_value == -1:
            if self.transition_flash:
                print("Starting flash")
                self.flash_value = 1
                return compute_flash(img)

        elif self.flash_value <= 0:
            print("Flash finished")
            self.flash_value = -1
            self.transition_flash = False
            return img

        elif self.flash_value > 0:
            self.flash_value -= 0.05

            return compute_flash(img)

    @staticmethod
    def get_video_from_number(number):
        """
        Returns the path to the video identified by it's number
        :param number:
        :return:
        """

        base_path = "videos/Compozitie mare "
        if not 0 <= number <= 5:
            exit("no video with number: " + number)

        else:
            return base_path + "{}.avi".format(number)
