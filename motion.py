import math 

def distance(a,b): 
    dx = a.x - b.x
    dy = a.y - b.y

    return math.sqrt((dx * dx) + (dy *dy)) 

class interpreter: 
    def __init__ (self,pinch_threshold = 0.06, open_threshold = 0.22): 
        self.pinch_threshold = pinch_threshold
        self.open_threshold = open_threshold
        self.last_gesture = "none"
    
    def interpreted(self,hands): 


        hand = hands[0] 
        lm = hand.landmark

        wrist = lm[0]
        thumb_tip = lm[4] 
        index_tip = lm[8] 
        middle_tip = lm[12]
        ring_tip = lm[16]
        pinky_tip = lm[20]

        index_knuckle = lm[5]
        middle_knuckle = lm[9]
        ring_knuckle = lm[13]
        pinky_knuckle = lm[17]

        x = index_tip.x
        y = index_tip.y

        def extended(tip,knuckle): 
            return distance(tip, wrist) > distance(knuckle,wrist)+0.02
        
        index_up = extended(index_tip, index_knuckle)
        middle_up = extended(middle_tip, middle_knuckle)
        ring_up = extended(ring_tip, ring_knuckle)
        pinky_up = extended(pinky_tip ,pinky_knuckle)

        pinch_detection = distance(thumb_tip,index_tip)
        pinch = pinch_detection< self.pinch_threshold

        pinch_strength = 0 #0 = no pinch, 1 = strong pinch 
        if pinch: 
            #clsoer the fingers the greater the pinch strength 
            pinch_strenth = max(0.0, min(1.0, 1.0- (pinch_detection/self.pinch_threshold)))
        
        openness =( distance(index_tip, wrist) + distance(middle_tip, wrist) + distance(ring_tip, wrist) + distance(pinky_tip, wrist)) / 4.0
        open = openness > self.open_threshold
        fist = (not index_up and not middle_up and not ring_up and not pinky_up) and (not open)


        # gesture classification 

        if pinch: 
            gesture = "pinch"
        elif fist: 
            gesture = "fist"
        elif open and index_up and middle_up and ring_up and pinky_up:
            gesture = "open"
        elif index_up and (not middle_up) and (not ring_up) and (not pinky_up):
            gesture = "point"
        elif index_up and middle_up and (not ring_up) and (not pinky_up):
            gesture = "peace"

        self.last_gesture = gesture 

        return {

            "gesture": gesture,
            "x": x,
            "y": y,
            "pinch": pinch,
            "pinch_strength": pinch_strength,
            "debug": {

                "openness": openness,
                "pinch_distance": pinch_detection,
                "index_up": index_up,
                "middle_up": middle_up,
                "ring_up": ring_up,
                "pinky_up": pinky_up,
            }
        }