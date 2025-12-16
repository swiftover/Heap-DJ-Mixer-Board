import pygame

from config import TRACK_A_PATH, TRACK_B_PATH, INITIAL_CROSSFADER, MASTER_VOLUME, SMOOTHING_FACTOR
import smoothing


class AudioEngine: 
    def __init__(self): 
        pygame.mixer.init()

        self.track_a = pygame.mixer.Sound(TRACK_A_PATH)
        self.track_b = pygame.mixer.Sound(TRACK_B_PATH)

        self.channel_a = self.track_a.play(loops = -1)
        self.channel_b = self.track_b.play(loops = -1)

        self.crossfader = INITIAL_CROSSFADER
        self.smooth_crossfader = self.crossfader
        self.master_volume = MASTER_VOLUME

        self.apply_crossfade() 


    def update(self, controls: dict):

        gesture = controls.get("gesture","none")
        x = controls.get("x", None)

        if x is None: 
            return 
        
        if gesture == "open":
            self.smooth_crossfader = smoothing.smooth_value(
                self.smooth_crossfader, x, SMOOTHING_FACTOR
            )
            self.crossfader = self.smooth_crossfader
            self.apply_crossfade()

        elif gesture == "fist":
            pass 

        else: 
            pass 
    def apply_crossfade(self):

        #0.0 = full a, 0 b, 1 = full b , 0 a

        if self.channel_a is None or self.channel_b is None: 
            return 
        
        volume_a = (1-self.crossfader) * self.master_volume
        volume_b = self.crossfader * self.master_volume 
        volume_a = max(0.0, min(1.0,volume_a))
        volume_b = max(0.0, min(1.0,volume_b))

    def shutdown(self): 
        pygame.mixer.stop()
        pygame.mixer.quit()
    
