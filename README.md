#Heap DJ Mixer Board
Gesture-controlled DJ mixer built with Python, OpenCV, MediaPipe, and Pygame.

## Overview
Heap DJ Mixer Board is a real-time DJ mixing application that replaces physical DJ hardware with **hand gestures captured through a webcam**. Hand movements are tracked using MediaPipe and OpenCV, interpreted as gestures, and mapped to audio controls in a dual-deck DJ system powered by Pygame.
The project focuses on **human–computer interaction**, **computer vision**, and **real-time audio control**.

---

## Features
- Real-time hand tracking via webcam
- Gesture-based audio control
- Dual-deck DJ mixer (Deck A & Deck B)
- Smooth crossfader with gain smoothing
- Fade-out → swap → fade-in track transitions
- Edge-triggered gestures (prevents accidental repeat skips)

---

## Gesture Controls

| Gesture | Action |
|------|------|
| Open hand | Control crossfader (left ↔ right) |
| Fist (left side) | Pause / resume Deck A |
| Fist (right side) | Pause / resume Deck B |
| Point (left side) | Load next track on Deck A | // STILL WIP
| Point (right side) | Load next track on Deck B | // STILL WIP
| Pinch | Reserved for future effects |

> Point gestures are edge-triggered, meaning they activate only once per gesture.

---
