import pygame

from config import TRACK_A_PATH, TRACK_B_PATH, INITIAL_CROSSFADER, MASTER_VOLUME, SMOOTHING_FACTOR
import smoothing


class AudioEngine: 
    def __init__(self): 
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)

        self.track_a = pygame.mixer.Sound(TRACK_A_PATH)
        self.track_b = pygame.mixer.Sound(TRACK_B_PATH)

        # Force specific channels (no auto allocation)
        self.channel_a = pygame.mixer.Channel(0)
        self.channel_b = pygame.mixer.Channel(1)

        self.channel_a.play(self.track_a, loops=-1)
        self.channel_b.play(self.track_b, loops=-1)

        self.crossfader = INITIAL_CROSSFADER
        self.smooth_crossfader = self.crossfader
        self.master_volume = MASTER_VOLUME

        self.deck_a_paused = False 
        self.deck_b_paused = False

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

        # FIST = pause based on side
        elif gesture == "fist" and x is not None:
            if x < 0.5:
                # LEFT → pause Deck A
                if not self.deck_a_paused:
                    self.channel_a.pause()
                    self.deck_a_paused = True
            else:
                # RIGHT → pause Deck B
                if not self.deck_b_paused:
                    self.channel_b.pause()
                    self.deck_b_paused = True

        # Not fist (or unknown) => resume anything that was paused
        else:
            if self.deck_a_paused:
                self.channel_a.unpause()
                self.deck_a_paused = False

            if self.deck_b_paused:
                self.channel_b.unpause()
                self.deck_b_paused = False




    def apply_crossfade(self):

        #0.0 = full a, 0 b, 1 = full b , 0 a
        # Clamp crossfader
        self.crossfader = max(0.0, min(1.0, float(self.crossfader)))

        volume_a = (1 - self.crossfader) * self.master_volume
        volume_b = self.crossfader * self.master_volume

        volume_a = max(0.0, min(1.0, volume_a))
        volume_b = max(0.0, min(1.0, volume_b))

        self.channel_a.set_volume(volume_a)
        self.channel_b.set_volume(volume_b)

        
    def shutdown(self): 
        pygame.mixer.stop()
        pygame.mixer.quit()
    
