#!/usr/bin/env python3
import argparse
import os
import subprocess
import shutil

def process_video(video_path, nth, workdir, result):
    print(f"\n{'='*60}")
    print(f"Processing: {video_path}")
    print(f"{'='*60}")

    # Step 1: Extract i-frames
    print("\n[1/3] Extracting i-frames...")
    cmd_extract = [
        'python3', 'extract_iframes_from_mp4.py',
        '--file', video_path,
        '--nth', str(nth),
        '--workdir', workdir
    ]
    subprocess.run(cmd_extract, check=True)

    # Step 2: Delete dark images
    print("\n[2/3] Deleting dark images...")
    cmd_delete = [
        'python3', 'delete_dark_images.py',
        '--workdir', workdir
    ]
    subprocess.run(cmd_delete, check=True)

    # Step 3: Collect selected images
    print("\n[3/3] Collecting selected images...")
    cmd_collect = [
        'python3', 'collect_selected_images.py',
        '--workdir', workdir,
        '--result', result
    ]
    subprocess.run(cmd_collect, check=True)

def find_mp4_files(source_dir):
    mp4_files = []

    for root, dirs, files in os.walk(source_dir):
        # Sort directories to process in alphabetical order
        dirs.sort()

        # Find MP4 files in current directory
        for file in sorted(files):
            if file.lower().endswith('.mp4'):
                mp4_files.append(os.path.join(root, file))

    return mp4_files

def main():
    parser = argparse.ArgumentParser(description='Process MP4 files recursively')
    parser.add_argument('--source', required=True, help='Source directory to process recursively')
    parser.add_argument('--nth', type=int, default=20, help='Extract every nth i-frame')
    parser.add_argument('--workdir', required=True, help='Working directory for temporary files')
    parser.add_argument('--result', required=True, help='Output MP4 file path')

    args = parser.parse_args()

    # Delete result file if it exists
    if os.path.exists(args.result):
        print(f"Deleting existing result file: {args.result}")
        os.remove(args.result)

    # Find all MP4 files
    mp4_files = find_mp4_files(args.source)

    if not mp4_files:
        print(f"No MP4 files found in {args.source}")
        return

    print(f"Found {len(mp4_files)} MP4 file(s) to process")

    # Process each MP4 file
    for i, mp4_file in enumerate(mp4_files, 1):
        print(f"\n\n### Processing file {i}/{len(mp4_files)} ###")

        try:
            process_video(mp4_file, args.nth, args.workdir, args.result)
        except Exception as e:
            print(f"Error processing {mp4_file}: {e}")
            continue

    print(f"\n\n{'='*60}")
    print(f"Processing complete!")
    print(f"Result saved to: {args.result}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
