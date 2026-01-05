#!/usr/bin/env python3
import argparse
import subprocess
import os
import tempfile

def collect_images_to_video(workdir, result):
    """Collect JPG files and append to MP4 result"""
    if not os.path.exists(workdir):
        print(f"Working directory {workdir} does not exist")
        return

    # Get all JPG files in alphabetical order
    jpg_files = sorted([f for f in os.listdir(workdir) if f.lower().endswith(('.jpg', '.jpeg'))])

    if not jpg_files:
        print("No JPG files found in working directory")
        return

    # Create a temporary file list for ffmpeg
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        list_file = f.name
        for jpg in jpg_files:
            # Write full path and escape single quotes
            full_path = os.path.abspath(os.path.join(workdir, jpg))
            f.write(f"file '{full_path}'\n")

    try:
        if os.path.exists(result):
            # Append to existing video
            # First create temp video from images
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

            cmd_create = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-r', '25',
                '-pix_fmt', 'yuv420p',
                '-y',
                temp_video
            ]
            subprocess.run(cmd_create, check=True)

            # Create concat list for existing and new video
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                concat_list = f.name
                f.write(f"file '{os.path.abspath(result)}'\n")
                f.write(f"file '{os.path.abspath(temp_video)}'\n")

            # Concat videos
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            cmd_concat = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                '-y',
                temp_output
            ]
            subprocess.run(cmd_concat, check=True)

            # Replace original with concatenated result
            os.replace(temp_output, result)

            # Cleanup
            os.unlink(temp_video)
            os.unlink(concat_list)
        else:
            # Create new video from images
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-r', '25',
                '-pix_fmt', 'yuv420p',
                '-y',
                result
            ]
            subprocess.run(cmd, check=True)

        print(f"Successfully saved/appended to {result}")
    finally:
        os.unlink(list_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collect JPG files into MP4 video')
    parser.add_argument('--workdir', required=True, help='Working directory containing JPEG files')
    parser.add_argument('--result', required=True, help='Output MP4 file path')

    args = parser.parse_args()
    collect_images_to_video(args.workdir, args.result)
