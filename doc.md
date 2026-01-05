I've created all five Python programs as requested:

## Individual Scripts:

1. **extract_iframes_from_mp4.py** - Extracts every nth i-frame from an MP4 file and saves them as JPGs
2. **delete_dark_images.py** - Scans JPEGs and deletes images with low saturation (dark images)
3. **collect_selected_images.py** - Collects JPG files and appends them to an MP4 video
4. **process.py** - Main orchestrator that processes directories recursively and calls the other scripts
5. **install.py** - Single installer file that creates all the scripts at once

## Key Features:

- All scripts have proper shebangs (`#!/usr/bin/env python3`)
- Proper argument parsing with `argparse`
- Alphabetical processing order maintained
- Working directory cleanup before processing
- Uses ffmpeg for video operations
- Uses Pillow (without numpy) for image analysis
- Appends to existing result MP4 if it exists
- Recursive directory processing

## Usage:

Run the installer first:
```bash
python3 install.py
```

Then process your videos:
```bash
python3 process.py --source ./videos --nth 20 --workdir ./temp --result output.mp4
```

The scripts will extract i-frames, filter out dark images, and compile the selected frames into a final video.
