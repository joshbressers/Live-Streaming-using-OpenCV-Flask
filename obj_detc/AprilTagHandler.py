import cv2
import numpy as np
from statistics import mean

class AprilTagHandler:
    "Class to make apriltag handling easier"

    def __init__(self, cv_handler):
        self.cv = cv_handler

