#!/usr/bin/env python3
"""
Installation script that creates all required Python scripts
"""
import os

SCRIPTS = {
    'extract_iframes_from_mp4.py': '''#!/usr/bin/env python3
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
        '-vf', f'select=eq(pict_type\\\\,I)*not(mod(n\\\\,{nth}))',
        '-vsync', 'vfr',
        output_pattern
    ]

    subprocess.run(cmd, check=True)
    print(f"Extracted I-frames to {workdir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract every nth I-frame from MP4 file')
    parser.add_argument('--file', required=True, help='Input MP4 file path')
    parser.add_argument('--nth', type=int, required=True, help='Extract every nth I-frame')
    parser.add_argument('--workdir', required=True, help='Working directory for output JPEGs')

    args = parser.parse_args()
    extract_iframes(args.file, args.nth, args.workdir)
''',

    'delete_dark_images.py': '''#!/usr/bin/env python3
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

    deleted_count = 0
    for filename in files:
        filepath = os.path.join(workdir, filename)
        try:
            saturation = calculate_saturation(filepath)
            if saturation < saturation_threshold:
                os.remove(filepath)
                deleted_count += 1
                print(f"Deleted {filename} (saturation: {saturation:.2f}%)")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Deleted {deleted_count} dark images")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete dark images based on saturation')
    parser.add_argument('--workdir', required=True, help='Working directory containing JPEG files')
    parser.add_argument('--saturation', type=float, default=5.0, help='Saturation threshold percentage (default: 5.0)')

    args = parser.parse_args()
    delete_dark_images(args.workdir, args.saturation)
''',

    'collect_selected_images.py': '''#!/usr/bin/env python3
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
            f.write(f"file '{full_path}'\\n")

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
                f.write(f"file '{os.path.abspath(result)}'\\n")
                f.write(f"file '{os.path.abspath(temp_video)}'\\n")

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
''',

    'process.py': '''#!/usr/bin/env python3
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
        print(f"\\n[{i}/{len(mp4_files)}] Processing: {mp4_file}")

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

    print(f"\\nAll processing complete. Result saved to: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MP4 files recursively')
    parser.add_argument('--source', required=True, help='Source directory to process recursively')
    parser.add_argument('--nth', type=int, required=True, help='Extract every nth I-frame')
    parser.add_argument('--workdir', required=True, help='Working directory for temporary files')
    parser.add_argument('--result', required=True, help='Output MP4 file path')

    args = parser.parse_args()
    process_videos(args.source, args.nth, args.workdir, args.result)
'''
}

def main():
    print("Video Processing Scripts Installer")
    print("=" * 50)

    for filename, content in SCRIPTS.items():
        print(f"Creating {filename}...", end=' ')
        try:
            with open(filename, 'w') as f:
                f.write(content)
            os.chmod(filename, 0o755)  # Make executable
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "=" * 50)
    print("Installation complete!")
    print("\nCreated files:")
    for filename in SCRIPTS.keys():
        print(f"  - {filename}")

    print("\nUsage example:")
    print("  python3 process.py --source ./videos --nth 20 --workdir ./temp --result output.mp4")
    print("\nRequirements:")
    print("  - ffmpeg (must be installed)")
    print("  - Pillow (pip install Pillow)")

if __name__ == "__main__":
    main()
