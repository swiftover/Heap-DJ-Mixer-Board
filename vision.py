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

    def process(self,frame): 
        #conversion from cv2 to mp         
        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        #hand track
        resultant = self.hands.process(rgb_frame)
        

        if resultant.multi_hands_landmarks: 
            self._last_landmarks = resultant.multi_hand_landmarks
            return resultant.multi_hand_landmarks
        self._last_landmarks = None 
        return None 
    
    def skeleton_marks(self,frame): 
        if self._last_landmarks is None: 
            return 
        
        for hand_landmarks in self._last_landmarks: 
            self.drawing_utils.draw_landmarks( 
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )



