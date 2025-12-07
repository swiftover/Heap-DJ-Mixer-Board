#Eduardo Nesta Gonzalez 
#Conjunction point for all the other files & will run everything 

import cv2 
from vision import HandTracker #from vision.py 
from audio_engine import AudioEngine # from audio_engine.py 
from gestures import GestureInterpreter #from gestures.py 


def main(): 
    hand_tracker = HandTracker()
    audio_engine = AudioEngine() 
    gesture_interpreter = GestureInterpreter()


    capture = cv2.VideCapture(0) #opens default camera 

    if not capture.VideoCapture(0):
        print("ERROR COULDNT OPEN DEFAULT CAMERA")
        return 
    print("Heap DJ Mixer is running, press q to quit")

    while True: 
        ret, frame = capture.read() #did the frame get captured correctly
        if not ret:
            print("ERROR: COULD NOT READ THE CAMERA FRAME")
            break

        frame = cv2.flip(frame,1) #mirror the frame so its equivalent to natural view

        hand_landmarks = hand_tracker.process(frame)
        
        if hand_landmarks:
            controls = gesture_interpreter.interpret(hand_landmarks)
            audio_engine.update_from_gestures(controls)

        hand_tracker.draw_landmarks(frame)

        cv2.imshow("Heap DJ Mixer, frame")

        if cv2.waitkey(1) & 0xFF == ord('q'):
            break 

    capture.release()
    cv2.destroyAllWindows()
    audio_engine.shutdown()

if __name__ == "__main__":
    main()
