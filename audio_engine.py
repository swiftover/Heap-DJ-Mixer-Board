# audio_engine.py
import pygame
import smoothing
import os

from config import (
    TRACK_A_PATH,
    TRACK_B_PATH,
    TRACK_A_QUEUE,
    TRACK_B_QUEUE,
    INITIAL_CROSSFADER,
    MASTER_VOLUME,
    SMOOTHING_FACTOR,
    DECK_TRANSITION_FADE,
)


class AudioEngine:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)

        # ---- Queues (fallback to single-track paths if lists are empty) ----
        self.queue_a = list(TRACK_A_QUEUE) if TRACK_A_QUEUE else [TRACK_A_PATH]
        self.queue_b = list(TRACK_B_QUEUE) if TRACK_B_QUEUE else [TRACK_B_PATH]
        self.idx_a = 0
        self.idx_b = 0

        self.track_a = pygame.mixer.Sound(self.queue_a[self.idx_a])
        self.track_b = pygame.mixer.Sound(self.queue_b[self.idx_b])

        # Force fixed channels (no auto allocation)
        self.channel_a = pygame.mixer.Channel(0)
        self.channel_b = pygame.mixer.Channel(1)

        # ---- Volume / gains ----
        self.master_volume = MASTER_VOLUME
        self.deck_a_gain = 1.0
        self.deck_b_gain = 1.0

        # ---- Crossfader ----
        self.crossfader = INITIAL_CROSSFADER
        self.target_crossfader = INITIAL_CROSSFADER

        # ---- Start audio ----
        self.channel_a.play(self.track_a, loops=-1)
        self.channel_b.play(self.track_b, loops=-1)
        self.apply_crossfade()

        # ---- Pause flags for fist gesture ----
        self.deck_a_paused = False
        self.deck_b_paused = False

        self._transition = None

    def update(self, controls: dict):
        # Progress fades / swaps
        self._process_transition()

        if not controls:
            return

        gesture = controls.get("gesture", "none")
        x = float(controls.get("x", 0.5))

        if controls.get("next_track", False):
            if x < 0.5:
                self._schedule_next_track("a")
            else:
                self._schedule_next_track("b")
            return

        # ----------------------------
        # OPEN HAND = crossfader control
        # ----------------------------
        if gesture == "open":
            self.target_crossfader = max(0.0, min(1.0, x))
            self.crossfader = smoothing.smooth_value(
                self.crossfader, self.target_crossfader, SMOOTHING_FACTOR
            )
            self.apply_crossfade()

        # ----------------------------
        # FIST = pause deck depending on side (left pauses A, right pauses B)
        # ----------------------------
        elif gesture == "fist":
            if x < 0.5:
                if not self.deck_a_paused:
                    self.channel_a.pause()
                    self.deck_a_paused = True
            else:
                if not self.deck_b_paused:
                    self.channel_b.pause()
                    self.deck_b_paused = True

        else:
            if self.deck_a_paused:
                self.channel_a.unpause()
                self.deck_a_paused = False

            if self.deck_b_paused:
                self.channel_b.unpause()
                self.deck_b_paused = False

    def apply_crossfade(self):
        volume_a = (1.0 - self.crossfader) * self.master_volume * self.deck_a_gain
        volume_b = self.crossfader * self.master_volume * self.deck_b_gain

        volume_a = max(0.0, min(1.0, volume_a))
        volume_b = max(0.0, min(1.0, volume_b))

        self.channel_a.set_volume(volume_a)
        self.channel_b.set_volume(volume_b)

    def _schedule_next_track(self, deck: str):
        deck = deck.lower().strip()
        if deck not in ("a", "b"):
            return

        if self._transition is not None:
            return

        # IMPORTANT: if the deck is paused, unpause it so you can HEAR the next track
        if deck == "a" and self.deck_a_paused:
            self.channel_a.unpause()
            self.deck_a_paused = False
        if deck == "b" and self.deck_b_paused:
            self.channel_b.unpause()
            self.deck_b_paused = False

        now = pygame.time.get_ticks()
        dur = int(DECK_TRANSITION_FADE)


        if deck == "a":
            self.crossfader = 0.0
            self.target_crossfader = 0.0
        else:
            self.crossfader = 1.0
            self.target_crossfader = 1.0
        self.apply_crossfade()

        if deck == "a":
            self._transition = {
                "deck": "a",
                "phase": "out",
                "t0": now,
                "dur": dur,
                "from_gain": float(self.deck_a_gain),
                "to_gain": 0.0,
            }
        else:
            self._transition = {
                "deck": "b",
                "phase": "out",
                "t0": now,
                "dur": dur,
                "from_gain": float(self.deck_b_gain),
                "to_gain": 0.0,
            }

        print(f"[AUDIO] next_track scheduled deck={deck}")

    def _process_transition(self):
        if self._transition is None:
            return

        now = pygame.time.get_ticks()
        t0 = self._transition["t0"]
        dur = max(1, int(self._transition["dur"]))
        phase = self._transition["phase"]
        deck = self._transition["deck"]
        from_gain = float(self._transition["from_gain"])
        to_gain = float(self._transition["to_gain"])

        p = (now - t0) / dur
        p = 0.0 if p < 0.0 else (1.0 if p > 1.0 else p)

        gain = from_gain + (to_gain - from_gain) * p
        if deck == "a":
            self.deck_a_gain = gain
        else:
            self.deck_b_gain = gain

        self.apply_crossfade()

        if p >= 1.0:
            if phase == "out":
                # Swap at silence, then fade back in
                if deck == "a":
                    self._swap_deck_a_track()
                else:
                    self._swap_deck_b_track()

                self._transition = {
                    "deck": deck,
                    "phase": "in",
                    "t0": now,
                    "dur": dur,
                    "from_gain": 0.0,
                    "to_gain": 1.0,
                }
            else:
                # Done
                if deck == "a":
                    self.deck_a_gain = to_gain
                else:
                    self.deck_b_gain = to_gain
                self.apply_crossfade()
                self._transition = None

    def _swap_deck_a_track(self):
        self.idx_a = (self.idx_a + 1) % len(self.queue_a)
        print("DEBUG: Deck A swapped to", os.path.basename(self.queue_a[self.idx_a]))
        self.track_a = pygame.mixer.Sound(self.queue_a[self.idx_a])

        self.channel_a.play(self.track_a, loops=-1)
        self.apply_crossfade()

    def _swap_deck_b_track(self):
        self.idx_b = (self.idx_b + 1) % len(self.queue_b)
        print("DEBUG: Deck B swapped to", os.path.basename(self.queue_b[self.idx_b]))
        self.track_b = pygame.mixer.Sound(self.queue_b[self.idx_b])

        self.channel_b.play(self.track_b, loops=-1)
        self.apply_crossfade()

    def shutdown(self):
        pygame.mixer.stop()
        pygame.mixer.quit()
