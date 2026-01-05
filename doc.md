I've created all five Python scripts as requested:

## Scripts Created:

1. **extract_iframes_from_mp4.py** - Extracts every nth I-frame from MP4 files
2. **delete_dark_images.py** - Removes images with low saturation (dark/desaturated images)
3. **collect_selected_images.py** - Combines JPG files into an MP4 video
4. **process.py** - Main orchestration script that processes directories recursively
5. **install.py** - Single-file installer that creates all the scripts

## Features:

- All scripts have proper shebangs (`#!/usr/bin/env python3`)
- Working directory is cleaned before processing
- Files are processed in alphabetical order
- Uses ffmpeg for video operations (no `-vsync` arg in collect script)
- Uses Pillow without numpy for saturation calculation
- Result MP4 is deleted before processing starts
- Appends to existing MP4 if it exists

## Usage:

```bash
# Install all scripts
python3 install.py

# Run the main processor
python3 process.py --source ./videos --nth 20 --workdir ./temp --result output.mp4
```

## Requirements:
- `ffmpeg` must be installed on your system
- Python package: `Pillow` (`pip install Pillow`)
