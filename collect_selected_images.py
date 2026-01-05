#!/usr/bin/env python3
import argparse
import subprocess
import os
import tempfile

def collect_images_to_video(workdir, result):
    # Get all JPG files in alphabetical order
    jpg_files = sorted([f for f in os.listdir(workdir) if f.lower().endswith(('.jpg', '.jpeg'))])

    if not jpg_files:
        print("No JPG files found in working directory")
        return

    print(f"Found {len(jpg_files)} images to process")

    # Create a temporary file list for ffmpeg
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        list_file = f.name
        for jpg_file in jpg_files:
            jpg_path = os.path.join(workdir, jpg_file)
            # Use absolute path and escape special characters
            abs_path = os.path.abspath(jpg_path)
            f.write(f"file '{abs_path}'\n")

    try:
        # Check if result file exists
        if os.path.exists(result):
            print(f"Appending to existing video: {result}")

            # Create temporary output for new images
            temp_new = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name

            # Convert new images to video at 25 fps
            cmd_new = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-r', '25',
                '-pix_fmt', 'yuv420p',
                '-y',
                temp_new
            ]
            subprocess.run(cmd_new, check=True, capture_output=True)

            # Create concat list for merging
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                merge_list = f.name
                f.write(f"file '{os.path.abspath(result)}'\n")
                f.write(f"file '{os.path.abspath(temp_new)}'\n")

            # Merge videos
            temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
            cmd_merge = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', merge_list,
                '-c', 'copy',
                '-y',
                temp_output
            ]
            subprocess.run(cmd_merge, check=True, capture_output=True)

            # Replace original with merged
            os.replace(temp_output, result)

            # Cleanup
            os.unlink(temp_new)
            os.unlink(merge_list)

        else:
            print(f"Creating new video: {result}")

            # Create directory for result if it doesn't exist
            result_dir = os.path.dirname(result)
            if result_dir:
                os.makedirs(result_dir, exist_ok=True)

            # Create video from images at 25 fps
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
            subprocess.run(cmd, check=True, capture_output=True)

        print(f"Successfully created/updated video: {result}")

    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        print(f"stderr: {e.stderr.decode()}")
    finally:
        # Cleanup list file
        if os.path.exists(list_file):
            os.unlink(list_file)

def main():
    parser = argparse.ArgumentParser(description='Collect JPG files into MP4 video')
    parser.add_argument('--workdir', required=True, help='Working directory with JPG files')
    parser.add_argument('--result', required=True, help='Output MP4 file path')

    args = parser.parse_args()

    collect_images_to_video(args.workdir, args.result)

if __name__ == '__main__':
    main()
