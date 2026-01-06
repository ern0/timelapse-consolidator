#!/usr/bin/env python3
import argparse
import subprocess
import os
import shutil

def extract_iframes(file_path, nth, workdir):
    # Create working directory if it doesn't exist
    os.makedirs(workdir, exist_ok=True)

    # Delete all files from working directory
    for filename in os.listdir(workdir):
        file_path_to_delete = os.path.join(workdir, filename)
        try:
            if os.path.isfile(file_path_to_delete):
                os.unlink(file_path_to_delete)
        except Exception as e:
            print(f"Error deleting {file_path_to_delete}: {e}")

    # Extract every nth I-frame using ffmpeg
    output_pattern = os.path.join(workdir, "frame_%05d.jpg")

    cmd = [
        'ffmpeg',
        '-i', file_path,
        '-vf', f'select=eq(pict_type\\,I)*not(mod(n\\,{nth}))',
        '-vsync', 'vfr',
        output_pattern
    ]

    with open('ffmpeg.log', 'a') as log:
        subprocess.run(cmd, check=True, stdout=log, stderr=subprocess.STDOUT)
    print(f"Extracted I-frames to {workdir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract every nth I-frame from MP4 file')
    parser.add_argument('--file', required=True, help='Input MP4 file path')
    parser.add_argument('--nth', type=int, required=True, help='Extract every nth I-frame')
    parser.add_argument('--workdir', required=True, help='Working directory for output JPEGs')

    args = parser.parse_args()
    extract_iframes(args.file, args.nth, args.workdir)
