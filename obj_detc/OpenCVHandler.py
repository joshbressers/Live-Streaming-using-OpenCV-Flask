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

    def get_frame(self, flipped=False):

        if flipped:
            return cv2.flip(self.frame, 1)
        else:
            return self.frame

    def get_hsv(self):
        self.hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        return self.hsv

    def get_gray(self):
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        return self.gray

    def get_height(self):
        if self.frame is None:
            self.update()
        return len(self.frame)

    def get_width(self):
        if self.frame is None:
            self.update()
        return len(self.frame[0])
