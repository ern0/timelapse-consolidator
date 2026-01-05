#!/usr/bin/env python3
"""
Convert JPG images from a directory to an MP4 video file.
Images are processed in alphabetical order.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def create_video_from_images(input_dir, output_file, fps=30):
    """
    Create an MP4 video from JPG images in a directory.
    
    Args:
        input_dir: Directory containing JPG images
        output_file: Output MP4 file path
        fps: Frames per second for the output video
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Directory '{input_dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Get all JPG files and sort alphabetically
    jpg_files = sorted(input_path.glob('*.jpg')) + sorted(input_path.glob('*.JPG'))
    
    if not jpg_files:
        print(f"Error: No JPG files found in '{input_dir}'", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(jpg_files)} JPG files")
    
    # Create a temporary file list for ffmpeg
    list_file = Path(output_file).parent / 'filelist.txt'
    
    try:
        with open(list_file, 'w') as f:
            for jpg in jpg_files:
                # Use absolute paths and escape single quotes
                abs_path = jpg.absolute()
                f.write(f"file '{abs_path}'\n")
                f.write(f"duration {1/fps}\n")
            # Add last image again for proper duration
            if jpg_files:
                f.write(f"file '{jpg_files[-1].absolute()}'\n")
        
        # Use ffmpeg to create video
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-vsync', 'vfr',
            '-pix_fmt', 'yuv420p',
            '-c:v', 'libx264',
            '-y',  # Overwrite output file
            str(output_file)
        ]
        
        print(f"Creating video: {output_file}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: ffmpeg failed with error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Successfully created video: {output_file}")
        
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg.", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up temporary file
        if list_file.exists():
            list_file.unlink()


def main():
    parser = argparse.ArgumentParser(
        description='Convert JPG images to MP4 video'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing JPG images'
    )
    parser.add_argument(
        'output_file',
        help='Output MP4 file path'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Frames per second (default: 30)'
    )
    
    args = parser.parse_args()
    
    create_video_from_images(args.input_dir, args.output_file, args.fps)


if __name__ == '__main__':
    main()
