import random
import time
import threading

import serial

from sys import platform


class PersonCounter:
    """
    Communicates to Arduino over serial communication and keeps track of the number of people.
    When the number of people changes, it will notify other listeners by changing 'number changed' to True.
    Listeners should set the variable to False after handling.
    """
    def __init__(self, port, no_arduino):
        self.people_count = 0
        self.number_changed = False

        self.keys = {"up": {"win32": 2490368, "darwin": 63232},
                     "down": {"win32": 2621440, "darwin": 63233}}

        if no_arduino:
            thread = threading.Thread(target=self.run_no_arduino, args=())
        else:
            self.serial = serial.Serial(port, baudrate=9600, timeout=0.1)
            thread = threading.Thread(target=self.run, args=())

        thread.start()

    def run(self):
        while True:
            arduino_data = self.serial.readline()
            if arduino_data:
                direction = arduino_data.decode("ascii")[0]
                if direction == "+":
                    self.people_count += 1
                elif direction == "-":
                    self.people_count -= 1
                else:
                    print("Bad Data From Arduino: " + str(arduino_data))

                self.correct()
                self.number_changed = True

    def run_no_arduino(self):
        while True:
            time.sleep(2)
            current_people_number = random.randint(0, 1)

            if not current_people_number == self.people_count:
                self.number_changed = True

            self.people_count = current_people_number

    def key(self, event):
        if event == -1:
            return

        print(event)

        if event == self.keys["up"][platform]:
            self.people_count += 1
            self.correct()
            self.number_changed = True
        if event == self.keys["down"][platform]:
            self.people_count -= 1
            self.correct()
            self.number_changed = True

        if 5 >= event - 48 >= 0:
            self.people_count = int(event - 48)
            self.correct()
            self.number_changed = True

    def correct(self):
        if self.people_count < 0:
            self.people_count = 0

        if self.people_count > 5:
            self.people_count = 5
