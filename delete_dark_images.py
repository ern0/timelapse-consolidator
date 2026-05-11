#!/usr/bin/env python3
import argparse
import os
from PIL import Image

def calculate_saturation(image_path):
    """Calculate median pixel saturation without numpy"""
    img = Image.open(image_path)

    # Convert to HSV to get saturation
    img_hsv = img.convert('HSV')

    # Get saturation channel (index 1)
    saturation_values = []
    width, height = img_hsv.size

    for y in range(height):
        for x in range(width):
            _, s, _ = img_hsv.getpixel((x, y))
            saturation_values.append(s)

    # Calculate median manually
    saturation_values.sort()
    n = len(saturation_values)
    if n % 2 == 0:
        median = (saturation_values[n//2 - 1] + saturation_values[n//2]) / 2
    else:
        median = saturation_values[n//2]

    # Convert to percentage (0-255 -> 0-100)
    return (median / 255.0) * 100

def delete_dark_images(workdir, saturation_threshold):
    """Delete images with saturation below threshold"""
    if not os.path.exists(workdir):
        print(f"Working directory {workdir} does not exist")
        return

    files = [f for f in os.listdir(workdir) if f.lower().endswith(('.jpg', '.jpeg'))]
    total = len(files)

    deleted_count = 0
    for index, filename in enumerate(files, start=1):
        filepath = os.path.join(workdir, filename)
        try:
            saturation = calculate_saturation(filepath)
            print(f"[{index}/{total}] {filename} (saturation: {saturation:.2f}%)", end="  \r")
            if saturation < saturation_threshold:
                os.remove(filepath)
                deleted_count += 1
        except Exception as e:
            print(f"\nError processing {filename}: {e}")

    if total > 0:
        print()
    print(f"Deleted {deleted_count} dark images")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete dark images based on saturation')
    parser.add_argument('--workdir', required=True, help='Working directory containing JPEG files')
    parser.add_argument('--saturation', type=float, default=5.0, help='Saturation threshold percentage (default: 5.0)')

    args = parser.parse_args()
    delete_dark_images(args.workdir, args.saturation)
