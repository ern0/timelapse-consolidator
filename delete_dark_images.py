#!/usr/bin/env python3
"""
Scan directory for JPG files and delete images with low saturation.
Deletes images where median pixel saturation is less than 10%.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import statistics


def rgb_to_hsv(r, g, b):
    """Convert RGB values (0-255) to HSV. Returns S as percentage (0-100)."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c

    # Saturation
    if max_c == 0:
        s = 0
    else:
        s = (diff / max_c) * 100

    return s


def calculate_median_saturation(image_path):
    """Calculate the median saturation of all pixels in an image."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Get all pixels
            pixels = list(img.getdata())

            # Calculate saturation for each pixel
            saturations = [rgb_to_hsv(r, g, b) for r, g, b in pixels]

            # Return median
            return statistics.median(saturations)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def process_directory(directory):
    """Scan directory and delete low-saturation JPG files."""
    directory = Path(directory)

    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return

    # Find all JPG files
    jpg_files = list(directory.glob("*.jpg")) + list(directory.glob("*.JPG")) + \
                list(directory.glob("*.jpeg")) + list(directory.glob("*.JPEG"))

    print(f"Found {len(jpg_files)} JPG files in {directory}")

    deleted_count = 0

    for img_file in jpg_files:
        median_sat = calculate_median_saturation(img_file)

        if median_sat is None:
            continue

        print(f"{img_file.name}: median saturation = {median_sat:.2f}%", end="")

        if median_sat < 10.0:
            try:
                os.remove(img_file)
                print(" -> DELETED")
                deleted_count += 1
            except Exception as e:
                print(f" -> Error deleting: {e}")
        else:
            print(" -> kept")

    print(f"\nProcessing complete. Deleted {deleted_count} image(s).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./script.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    process_directory(target_dir)
