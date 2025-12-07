import cv2 
import mediapipe as mp 

class HandTracker: 
    def __init__(self, max_num_hands = 2, detection_confidence = 0.5, tracking_confidence = 0.5): 
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands = max_num_hands,
            min_dc = detection_confidence,
            min_tc = tracking_confidence,
        )
    self.drawing_utils = mp.solutions.drawing_utils # draws the hand overlay 

    self._last_landmarks = None # store detected hand land mark 