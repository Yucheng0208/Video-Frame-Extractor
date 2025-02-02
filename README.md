# Extract Frames from Videos

## Overview
This Python script extracts frames from video files at a specified frame rate (FPS) and saves them as PNG images. The script processes all video files in the input directory and organizes the extracted frames into subdirectories for each video.

## Features
- Supports multiple video formats (`.mp4`, `.avi`, `.mov`, `.mkv`).
- Allows users to specify the desired FPS for frame extraction.
- Creates a dedicated output directory for each video file.
- Uses `tqdm` for a progress bar while processing videos.

## Requirements
Ensure you have the following dependencies installed:
```pip install opencv-python tqdm```

## Usage
Run the script using Python:
```python extract_frames.py```
The script will prompt for:
- **Input directory:** The directory containing video files.
- **Output directory:** The directory where extracted frames will be saved.
- **Desired FPS:** The frame rate for extraction (e.g., five frames per second).

## Example
1. Assume the following directory structure before running the script:
```
/videos
   ├── video1.mp4
   ├── video2.avi
```
2. Running the script and providing the `/videos` directory as input and `/frames` as output:
```
Enter the input directory containing videos: /videos
Enter the output directory for extracted frames: /frames
Enter the desired frames per second (FPS): 5
```
3. The extracted frames will be saved in:
```
/frames
   ├── video1
   │   ├── frame_0000.png
   │   ├── frame_0001.png
   ├── video2
       ├── frame_0000.png
       ├── frame_0001.png
```
## Code Explanation
The script performs the following steps:
1. Reads video files from the input directory.
2. Extracts frames at the specified FPS.
3. Saves frames as PNG images in subdirectories named after the original videos.
4. Uses `tqdm` to display a progress bar.
5. Handles exceptions and invalid input directories.

## LICENSE
This project is licensed under the [MIT License](LICENSE).
