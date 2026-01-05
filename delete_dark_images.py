#!/usr/bin/env python3
import argparse
import os
from PIL import Image

def calculate_median_saturation(image_path):
    try:
        img = Image.open(image_path)

        # Convert to HSV to get saturation
        hsv_img = img.convert('HSV')

        # Get saturation channel (index 1)
        pixels = list(hsv_img.getdata())
        saturations = [p[1] for p in pixels]

        # Calculate median manually without numpy
        sorted_saturations = sorted(saturations)
        n = len(sorted_saturations)

        if n % 2 == 0:
            median = (sorted_saturations[n//2 - 1] + sorted_saturations[n//2]) / 2.0
        else:
            median = sorted_saturations[n//2]

        # Convert to percentage (HSV saturation is 0-255)
        median_percent = (median / 255.0) * 100.0

        return median_percent
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def delete_dark_images(workdir, saturation_threshold):
    deleted_count = 0
    processed_count = 0

    # Get all JPEG files sorted
    files = sorted([f for f in os.listdir(workdir) if f.lower().endswith(('.jpg', '.jpeg'))])

    for filename in files:
        file_path = os.path.join(workdir, filename)
        processed_count += 1

        median_saturation = calculate_median_saturation(file_path)

        if median_saturation is not None:
            if median_saturation < saturation_threshold:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted {filename} (saturation: {median_saturation:.2f}%)")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
            else:
                print(f"Kept {filename} (saturation: {median_saturation:.2f}%)")

    print(f"\nProcessed {processed_count} images, deleted {deleted_count}")

def main():
    parser = argparse.ArgumentParser(description='Delete dark images based on saturation')
    parser.add_argument('--workdir', required=True, help='Working directory with JPEG files')
    parser.add_argument('--saturation', type=float, default=10.0, help='Saturation threshold percentage')

    args = parser.parse_args()

    delete_dark_images(args.workdir, args.saturation)

if __name__ == '__main__':
    main()
