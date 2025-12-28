# config.py
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKS_DIR = os.path.join(BASE_DIR, "tracks")

TRACK_A_PATH = os.path.join(TRACKS_DIR, "song1.wav")
TRACK_B_PATH = os.path.join(TRACKS_DIR, "song2.wav")


TRACK_A_QUEUE = [
    os.path.join(TRACKS_DIR, "song1.wav"),
    os.path.join(TRACKS_DIR, "song3.wav"),
    os.path.join(TRACKS_DIR, "song5.wav"),
    os.path.join(TRACKS_DIR, "song7.wav"),
]

TRACK_B_QUEUE = [
    os.path.join(TRACKS_DIR, "song2.wav"),
    os.path.join(TRACKS_DIR, "song4.wav"),
    os.path.join(TRACKS_DIR, "song6.wav"),
    os.path.join(TRACKS_DIR, "song8.wav"),
]

MASTER_VOLUME = 0.8          # 0.0 – 1.0
INITIAL_CROSSFADER = 0.5     # 0.0 = full A, 1.0 = full B
DECK_TRANSITION_FADE = 800   # milliseconds

SMOOTHING_FACTOR = 0.7


for path in [TRACK_A_PATH, TRACK_B_PATH] + TRACK_A_QUEUE + TRACK_B_QUEUE:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing audio file: {path}")
