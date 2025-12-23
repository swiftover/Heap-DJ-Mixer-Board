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

        # True while we're currently in point gesture (prevents spam swapping)
        self._point_latched = False

        # ---- Fade-out → swap → fade-in scheduling ----
        self._pending_swap_a_due_ms = None
        self._pending_swap_b_due_ms = None

    def update(self, controls: dict):

        # Process pending swaps (if fade-out finished)
        self._process_pending_swaps()

        if not controls:
            # If controls are missing, treat as "not pointing" so latch resets
            self._point_latched = False
            return

        gesture = controls.get("gesture", "none")
        x = float(controls.get("x", 0.5))

        # FIX 1: latch should ONLY stay True while we are actively pointing
        if gesture != "point":
            self._point_latched = False

        # OPEN HAND = crossfader control
        if gesture == "open":
            self.target_crossfader = max(0.0, min(1.0, x))
            self.crossfader = smoothing.smooth_value(
                self.crossfader, self.target_crossfader, SMOOTHING_FACTOR
            )
            self.apply_crossfade()

        # FIST = pause deck depending on side (left pauses A, right pauses B)
        elif gesture == "fist":
            if x < 0.5:
                if not self.deck_a_paused:
                    self.channel_a.pause()
                    self.deck_a_paused = True
            else:
                if not self.deck_b_paused:
                    self.channel_b.pause()
                    self.deck_b_paused = True

        # POINT = trigger next track per side ONCE per point gesture
        elif gesture == "point":
            if not self._point_latched:
                if x < 0.5:
                    self._schedule_next_track("a")  # point LEFT
                else:
                    self._schedule_next_track("b")  # point RIGHT
                self._point_latched = True

            # (do NOT resume paused decks here; point can be used while paused)

        # anything else = resume (and latch already reset above)
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
        """Fade out the chosen deck, then swap to the next track in that deck's queue."""
        deck = deck.lower().strip()
        now = pygame.time.get_ticks()

        if deck == "a":
            if self._pending_swap_a_due_ms is not None:
                return
            self.channel_a.fadeout(DECK_TRANSITION_FADE)
            self._pending_swap_a_due_ms = now + DECK_TRANSITION_FADE

        elif deck == "b":
            if self._pending_swap_b_due_ms is not None:
                return
            self.channel_b.fadeout(DECK_TRANSITION_FADE)
            self._pending_swap_b_due_ms = now + DECK_TRANSITION_FADE

    def _process_pending_swaps(self):
        now = pygame.time.get_ticks()

        if self._pending_swap_a_due_ms is not None and now >= self._pending_swap_a_due_ms:
            self._pending_swap_a_due_ms = None
            self._advance_deck_a()

        if self._pending_swap_b_due_ms is not None and now >= self._pending_swap_b_due_ms:
            self._pending_swap_b_due_ms = None
            self._advance_deck_b()

    def _advance_deck_a(self):
        self.idx_a = (self.idx_a + 1) % len(self.queue_a)

        print("DEBUG: Deck A swapped to",
            os.path.basename(self.queue_a[self.idx_a]))

        self.track_a = pygame.mixer.Sound(self.queue_a[self.idx_a])

        # FIX 3: ensure pause state is correct BEFORE play()
        if self.deck_a_paused:
            self.channel_a.pause()
        else:
            self.channel_a.unpause()

        # IMPORTANT: set the correct target volume BEFORE fade-in starts
        self.apply_crossfade()

        # Now play with fade-in (it will fade to the current channel volume)
        self.channel_a.play(self.track_a, loops=-1, fade_ms=DECK_TRANSITION_FADE)



    def _advance_deck_b(self):
        self.idx_b = (self.idx_b + 1) % len(self.queue_b)

        print("DEBUG: Deck B swapped to",
            os.path.basename(self.queue_b[self.idx_b]))

        self.track_b = pygame.mixer.Sound(self.queue_b[self.idx_b])

        # FIX 3: ensure pause state is correct BEFORE play()
        if self.deck_b_paused:
            self.channel_b.pause()
        else:
            self.channel_b.unpause()

        # IMPORTANT: set the correct target volume BEFORE fade-in starts
        self.apply_crossfade()

        # Now play with fade-in (it will fade to the current channel volume)
        self.channel_b.play(self.track_b, loops=-1, fade_ms=DECK_TRANSITION_FADE)
        print("DEBUG busy B:", self.channel_b.get_busy(), "vol:", self.channel_b.get_volume())


    def shutdown(self):
        pygame.mixer.stop()
        pygame.mixer.quit()
