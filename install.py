#!/usr/bin/env python3
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

    # Extract every nth i-frame using ffmpeg
    output_pattern = os.path.join(workdir, "frame_%06d.jpg")

    cmd = [
        'ffmpeg',
        '-i', file_path,
        '-vf', f'select=eq(pict_type\\\\,I)*not(mod(n\\\\,{nth}))',
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
''',

    'delete_dark_images.py': '''#!/usr/bin/env python3
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

    print(f"\\nProcessed {processed_count} images, deleted {deleted_count}")

def main():
    parser = argparse.ArgumentParser(description='Delete dark images based on saturation')
    parser.add_argument('--workdir', required=True, help='Working directory with JPEG files')
    parser.add_argument('--saturation', type=float, default=10.0, help='Saturation threshold percentage')

    args = parser.parse_args()

    delete_dark_images(args.workdir, args.saturation)

if __name__ == '__main__':
    main()
''',

    'collect_selected_images.py': '''#!/usr/bin/env python3
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
            f.write(f"file '{abs_path}'\\n")

    try:
        # Check if result file exists
        if os.path.exists(result):
            print(f"Appending to existing video: {result}")

            # Create temporary output for new images
            temp_new = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name

            # Convert new images to video
            cmd_new = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-vf', 'fps=1',
                '-pix_fmt', 'yuv420p',
                '-y',
                temp_new
            ]
            subprocess.run(cmd_new, check=True, capture_output=True)

            # Create concat list for merging
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                merge_list = f.name
                f.write(f"file '{os.path.abspath(result)}'\\n")
                f.write(f"file '{os.path.abspath(temp_new)}'\\n")

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

            # Create video from images
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-vf', 'fps=1',
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
''',

    'process.py': '''#!/usr/bin/env python3
import argparse
import os
import subprocess
import shutil

def process_video(video_path, nth, workdir, result):
    print(f"\\n{'='*60}")
    print(f"Processing: {video_path}")
    print(f"{'='*60}")

    # Step 1: Extract i-frames
    print("\\n[1/3] Extracting i-frames...")
    cmd_extract = [
        'python3', 'extract_iframes_from_mp4.py',
        '--file', video_path,
        '--nth', str(nth),
        '--workdir', workdir
    ]
    subprocess.run(cmd_extract, check=True)

    # Step 2: Delete dark images
    print("\\n[2/3] Deleting dark images...")
    cmd_delete = [
        'python3', 'delete_dark_images.py',
        '--workdir', workdir
    ]
    subprocess.run(cmd_delete, check=True)

    # Step 3: Collect selected images
    print("\\n[3/3] Collecting selected images...")
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
        print(f"\\n\\n### Processing file {i}/{len(mp4_files)} ###")

        try:
            process_video(mp4_file, args.nth, args.workdir, args.result)
        except Exception as e:
            print(f"Error processing {mp4_file}: {e}")
            continue

    print(f"\\n\\n{'='*60}")
    print(f"Processing complete!")
    print(f"Result saved to: {args.result}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
'''
}

def main():
    print("Installing video processing scripts...")
    print("="*60)

    for filename, content in SCRIPTS.items():
        print(f"Creating {filename}...")

        with open(filename, 'w') as f:
            f.write(content)

        # Make executable
        os.chmod(filename, 0o755)

        print(f"  ✓ {filename} created and made executable")

    print("="*60)
    print("Installation complete!")
    print("\nCreated files:")
    for filename in SCRIPTS.keys():
        print(f"  - {filename}")

    print("\nUsage example:")
    print("  python3 process.py --source ./videos --nth 20 --workdir ./temp --result output.mp4")

if __name__ == '__main__':
    main()
