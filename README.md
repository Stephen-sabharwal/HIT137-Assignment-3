# Spot the Difference Game (Python + Tkinter + OpenCV)
## University Assignment Submission
This project is a desktop **Spot the Difference** game built using:
- **Python**
- **Tkinter** (GUI)
- **OpenCV** (image processing)
- **OOP design** (class-based architecture)

The application loads an image, generates a modified copy with exactly **5 non-overlapping differences**, and lets the player find those differences by clicking on the modified image.

## Features
- Load images in **JPG / PNG / BMP** format.
- Display two images side by side:
  - **Left:** Original image
  - **Right:** Modified image
- Automatically generate **exactly 5 differences** every time a new image is loaded.
- Differences are:
  - Randomly placed
  - Non-overlapping
  - Freshly generated for each round
- Implemented difference types:
  1. Color shift
  2. Blur region
  3. Brightness change
- Gameplay rules:
  - User clicks only on the modified (right) image
  - Correct click: marks difference as found and draws **red circles** on both images
  - Wrong click: increases mistake count
  - Maximum mistakes = **3**
  - At 3 mistakes, game ends and further clicks are disabled
  - Finding all 5 differences shows a success message
- **Reveal Remaining** button:
  - Reveals unfound differences with **blue circles** on both images
- **Reset Game**:
  - Regenerates a new round and resets score/mistakes/difference state

## Project Structure
```text
project/
├── main.py
├── README.md
├── requirements.txt
├── github_link.txt
├── gui/
│   ├── __init__.py
│   └── game_app.py
├── logic/
│   ├── __init__.py
│   └── game_logic.py
├── processing/
│   ├── __init__.py
│   └── image_processor.py
├── models/
│   ├── __init__.py
│   └── difference_region.py
└── assets/
    └── sample_images/
        └── README.txt
```

## OOP Design (Required Classes)
The project follows class-based encapsulation and separation of responsibilities:

1. **GameApp** (`gui/game_app.py`)
   - Tkinter UI controller
   - Handles file loading, click events, rendering images, button actions
   - Coordinates between logic and processing layers

2. **ImageProcessor** (`processing/image_processor.py`)
   - OpenCV image loading and transformation
   - Generates exactly 5 random, non-overlapping difference regions
   - Applies visual modifications (color/blur/brightness)

3. **GameLogic** (`logic/game_logic.py`)
   - Manages game rules and state
   - Tracks mistakes, found/remaining differences, win/lose conditions
   - Evaluates clicks with tolerance

4. **DifferenceRegion** (`models/difference_region.py`)
   - Data model for each difference region
   - Stores center, radius, type, and found-state
   - Provides overlap and hit-detection methods

## Requirements
- Python 3.10+ recommended
- Pip package manager

Install dependencies:
```powershell
pip install -r requirements.txt
```

`requirements.txt` includes:
- `opencv-python`
- `numpy`
- `Pillow`

## How to Run
From the `project/` directory:
```powershell
python main.py
```

## Gameplay Instructions
1. Click **Load Image** and select a JPG/PNG/BMP image.
2. Compare left and right images.
3. Click suspected differences on the **right image only**.
4. Find all 5 differences before reaching 3 mistakes.
5. Use **Reveal Remaining** if needed.
6. Use **Reset Game** to start a fresh round.

## Notes for Testing
- Place sample images in `assets/sample_images/` for easy testing.
- Recommended image quality:
  - At least **800x600**
  - Moderate visual detail (campus, street, room, landscape)

## Packaging for Submission (ZIP)
Create the ZIP from the parent folder containing `project/`.

### PowerShell (Windows)
```powershell
Compress-Archive -Path .\project\* -DestinationPath .\assignment3.zip -Force
```

### Git Bash / Linux / macOS
```bash
zip -r assignment3.zip project/
```

## Deliverables Checklist
- [x] Complete source code with OOP structure
- [x] Tkinter GUI with side-by-side image display
- [x] OpenCV-based generation of 5 non-overlapping differences
- [x] Gameplay logic with scoring, mistakes, win/lose conditions
- [x] Reveal feature and reset behavior
- [x] Dependency file (`requirements.txt`)
- [x] Submission documentation (`README.md`)

