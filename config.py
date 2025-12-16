import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- AUDIO FILE PATHS ----
TRACKS_DIR = os.path.join(BASE_DIR, "tracks")

TRACK_A_PATH = os.path.join(TRACKS_DIR, "song1.wav")
TRACK_B_PATH = os.path.join(TRACKS_DIR, "song2.wav")

# ---- AUDIO SETTINGS ----
MASTER_VOLUME = 0.8          # 0..1
INITIAL_CROSSFADER = 0.5     # start in the middle

# ---- GESTURE SETTINGS ----
SMOOTHING_FACTOR = 0.7       # higher = smoother, slower
