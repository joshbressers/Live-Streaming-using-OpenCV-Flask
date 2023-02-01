import cv2
import numpy as np
from statistics import mean

class OpenCVHandler:
    "Class to make opencv easier"

    def __init__(self):
        self.frame = None
        self.hsv = None
        self.camera = cv2.VideoCapture(0)

    def update(self):
        success, frame = self.camera.read()
        if success:
            self.frame = frame
            self.hsv = None
            self.gray = None

    def get_frame(self, flipped=False):

        if flipped:
            return cv2.flip(self.frame, 1)
        else:
            return self.frame

    def get_hsv(self):
        if self.hsv is None:
            self.hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        return self.hsv

    def get_gray(self):
        if self.gray is None:
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        return self.gray

    def get_height(self):
        return len(self.frame)

    def get_width(self):
        return len(self.frame[0])

    def add_rectangle(self, start, end, color, thickness=2):
        self.frame = cv2.rectangle(self.frame, start, end, color, thickness)

    def get_jpg_bytes(self, flipped=False):
        frame = self.get_frame(flipped)
        ret, buffer = cv2.imencode('.jpg', frame)
        jpg = buffer.tobytes()
        return jpg
