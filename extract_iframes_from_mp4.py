#!/usr/bin/env python3
"""
Extract I-frames from MP4 video files and save as JPEG images.
Requires: ffmpeg-python (install with: pip install ffmpeg-python)
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def extract_iframes(video_path, output_dir, nth_frame=10):
    """
    Extract every Nth I-frame from video and save as JPEG.

    Args:
        video_path: Path to input MP4 file
        output_dir: Directory to save extracted frames
        nth_frame: Extract every Nth I-frame (default: 10)
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verify input file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found")
        sys.exit(1)

    # Output pattern for frames
    output_pattern = output_dir / "iframe_%04d.jpg"

    # Build ffmpeg command
    # -skip_frame nokey: Only decode I-frames (key frames)
    # select='not(mod(n\,{nth_frame}))': Select every Nth frame
    cmd = [
        'ffmpeg',
        '-skip_frame', 'nokey',  # Only process I-frames
        '-i', video_path,
        '-vf', f"select='not(mod(n\\,{nth_frame}))'",  # Select every Nth I-frame
        '-vsync', 'vfr',  # Variable frame rate (prevents duplicate frames)
        '-q:v', '2',  # JPEG quality (2 is high quality, 1-31 range)
        str(output_pattern)
    ]

    print(f"Extracting every {nth_frame}th I-frame from: {video_path}")
    print(f"Output directory: {output_dir}")
    print(f"Running command: {' '.join(cmd)}\n")

    try:
        # Run ffmpeg command
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        # Count extracted frames
        frame_count = len(list(output_dir.glob("iframe_*.jpg")))
        print(f"\nSuccessfully extracted {frame_count} I-frames")
        print(f"Frames saved to: {output_dir}")

    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Extract I-frames from MP4 video files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s video.mp4 output_frames
  %(prog)s video.mp4 output_frames --nth 5
  %(prog)s input.mp4 ./frames -n 20
        """
    )

    parser.add_argument(
        'video',
        help='Path to input MP4 file'
    )

    parser.add_argument(
        'output_dir',
        help='Directory to save extracted frames (will be created if needed)'
    )

    parser.add_argument(
        '-n', '--nth',
        type=int,
        default=10,
        metavar='N',
        help='Extract every Nth I-frame (default: 10)'
    )

    args = parser.parse_args()

    # Validate nth_frame
    if args.nth < 1:
        print("Error: --nth must be >= 1")
        sys.exit(1)

    extract_iframes(args.video, args.output_dir, args.nth)


if __name__ == '__main__':
    main()
