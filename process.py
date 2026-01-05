#!/usr/bin/env python3
import argparse
import subprocess
import os
import shutil

def process_videos(source, nth, workdir, result):
    """Process all MP4 files recursively in alphabetical order"""

    # Delete result file if it exists
    if os.path.exists(result):
        os.remove(result)
        print(f"Deleted existing result file: {result}")

    # Find all MP4 files recursively and sort them
    mp4_files = []
    for root, dirs, files in os.walk(source):
        # Sort directories and files for consistent alphabetical order
        dirs.sort()
        files.sort()

        for file in files:
            if file.lower().endswith('.mp4'):
                mp4_files.append(os.path.join(root, file))

    mp4_files.sort()

    if not mp4_files:
        print(f"No MP4 files found in {source}")
        return

    print(f"Found {len(mp4_files)} MP4 files to process")

    for i, mp4_file in enumerate(mp4_files, 1):
        print(f"\n[{i}/{len(mp4_files)}] Processing: {mp4_file}")

        try:
            # Step 1: Extract I-frames
            print("  Extracting I-frames...")
            subprocess.run([
                'python3',
                'extract_iframes_from_mp4.py',
                '--file', mp4_file,
                '--nth', str(nth),
                '--workdir', workdir
            ], check=True)

            # Step 2: Delete dark images
            print("  Deleting dark images...")
            subprocess.run([
                'python3',
                'delete_dark_images.py',
                '--workdir', workdir
            ], check=True)

            # Step 3: Collect selected images
            print("  Collecting images to video...")
            subprocess.run([
                'python3',
                'collect_selected_images.py',
                '--workdir', workdir,
                '--result', result
            ], check=True)

            print(f"  ✓ Completed processing {mp4_file}")

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Error processing {mp4_file}: {e}")
            continue

    print(f"\nAll processing complete. Result saved to: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MP4 files recursively')
    parser.add_argument('--source', required=True, help='Source directory to process recursively')
    parser.add_argument('--nth', type=int, required=True, help='Extract every nth I-frame')
    parser.add_argument('--workdir', required=True, help='Working directory for temporary files')
    parser.add_argument('--result', required=True, help='Output MP4 file path')

    args = parser.parse_args()
    process_videos(args.source, args.nth, args.workdir, args.result)
