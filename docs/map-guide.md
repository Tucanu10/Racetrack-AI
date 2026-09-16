<div align="center">
  <h1>Racetrack<kbd>AI</kbd></h1>
  <p><b>Custom Map-Making Guide</b></p>
  <p><i>Learn how to design, configure, and train autonomous agents on your own custom racing circuits.</i></p>
</div>

---

## 🗺️ Overview

Creating a new circuit for the AI to train on is straightforward. The system relies on Pygame's alpha masking for collision detection and bounding boxes for fitness checkpoints.

---

## Step 1: Draw the Track Image

*   Create a new folder for your map inside `src/` (e.g., `src/map1/`).
*   Draw your track and save it as `map.png` with an exact resolution of **1080x720**.
<p style="color">**Crucial Rule:** The drivable road surface **MUST be completely transparent**. The engine's raycasting and collision systems treat any non-transparent pixel as a solid wall.

---

## Step 2: Define the Checkpoints & Start Position

The AI calculates its fitness based on the distance to the next checkpoint. You need to define these as invisible trigger zones, along with the car's initial spawn coordinates.

*   Create a `checkpoints.py` file in your new map folder.
*   Define a `START_POS` tuple with the `(x, y)` pixel coordinates where the cars should spawn.
*   Define a sequential list of `pygame.Rect` objects, starting from the start line and ending at the finish line.

```python
# src/map1/checkpoints.py
import pygame

# Starting coordinates for the cars (x, y)
START_POS = (100, 200)

# Checkpoints defined as pygame.Rect(left, top, width, height)
checkpoints = [
    pygame.Rect(0, 180, 140, 20),   # Checkpoint 1 (Start line)
    pygame.Rect(180, 0, 20, 140),   # Checkpoint 2
    # ... add your custom coordinates here
    pygame.Rect(0, 315, 140, 20)    # Checkpoint N (Finish line)
]
```

## Step 3: Changing the Map

* Open `src/config.conf`
* Change the *ACTIVE_MAP* variable to your new map folder name:
```python
ACTIVE_MAP = "mapName"
```

## Step 4: Test and Train
* If you wish to try the map yourself, you can always run
```bash
make play
```
* You will be placed on the map with a controllable car via
```bash
W - forward
A / D - turning
S - Brake
F3 - Debug Menu
```

* Once you are satisfied with your track and your checkpoints are well placed, you can start training
```bash
make train
```
* This will load your new map asset, spawn the 200 autonomous agents, and begin the evolutionary training process on your custom circuit.