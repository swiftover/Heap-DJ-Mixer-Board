#Eduardo Nesta Gonzalez 
#Conjunction point for all the other files & will run everything 

import cv2 
from vision import HandTracker #from vision.py 
from audio_engine import AudioEngine # from audio_engine.py 
from motion import interpreter #from motion.py 


def main(): 
    hand_tracker = HandTracker()
    audio_engine = AudioEngine() 
    gesture_interpreter = interpreter()


    capture = cv2.VideoCapture(0) #opens default camera 

    if not capture.isOpened():
        print("ERROR COULDNT OPEN DEFAULT CAMERA")
        return 
    print("Heap DJ Mixer is running, press q to quit")

    while True:
        ret, frame = capture.read()
        if not ret:
            print("ERROR: COULD NOT READ THE CAMERA FRAME")
            break

        frame = cv2.flip(frame, 1)

        hand_landmarks = hand_tracker.process(frame)

        if hand_landmarks:
            controls = gesture_interpreter.interpret(hand_landmarks)
            audio_engine.update(controls)

        hand_tracker.draw_landmarks(frame)

        cv2.imshow("Heap DJ Mixer", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()
    audio_engine.shutdown()

if __name__ == "__main__":
    main()
