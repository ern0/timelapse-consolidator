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

    # Extract every nth i-frame using ffmpeg
    output_pattern = os.path.join(workdir, "frame_%06d.jpg")

    cmd = [
        'ffmpeg',
        '-i', file_path,
        '-vf', f'select=eq(pict_type\\,I)*not(mod(n\\,{nth}))',
        '-vsync', '0',
        '-q:v', '2',
        output_pattern
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Successfully extracted i-frames from {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print(f"stderr: {e.stderr.decode()}")

def main():
    parser = argparse.ArgumentParser(description='Extract every nth i-frame from MP4 file')
    parser.add_argument('--file', required=True, help='Input MP4 file path')
    parser.add_argument('--nth', type=int, default=20, help='Extract every nth i-frame')
    parser.add_argument('--workdir', required=True, help='Working directory for output JPGs')

    args = parser.parse_args()

    extract_iframes(args.file, args.nth, args.workdir)

if __name__ == '__main__':
    main()
