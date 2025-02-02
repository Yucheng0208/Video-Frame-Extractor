# Video Frame Extractor

## Overview
This Python script extracts frames from video files at a specified frame rate (FPS) and saves them in the desired image format (`.jpg`, `.jpeg`, `.png`, `.tif`). The script can be run interactively or with command-line parameters.

## Features
- Supports multiple video formats (`.mp4`, `.avi`, `.mov`, `.mkv`).
- Allows users to specify the desired FPS for frame extraction.
- Supports multiple output image formats (`.jpg`, `.jpeg`, `.png`, `.tif`).
- Provides an interactive prompt if no command-line arguments are given.
- Uses `tqdm` for progress tracking.

## Requirements
Ensure you have the following dependencies installed:
```bash
pip install opencv-python tqdm
```

## Usage
### Run with Interactive Mode
Run the script using Python:
```bash
python Video-Frame-Extractor.py
```
The script will prompt for:
- **Input directory:** The directory containing video files.
- **Output directory:** The directory where extracted frames will be saved.
- **Desired FPS:** The frame rate for extraction.
- **Output Image Format:** Users can choose between `.jpg`, `.jpeg`, `.png`, `.tif`.

### Run with Command-Line Parameters
Alternatively, users can provide all parameters in one command:
```bash
python Video-Frame-Extractor.py --input_dir path/to/videos --output_dir path/to/output --fps 5 --img_format jpg
```

### Example
1. Assume the following directory structure before running the script:
```
/videos
   ├── video1.mp4
   ├── video2.avi
```
2. Running the script interactively and providing the `/videos` directory as input and `/frames` as output:
```
Enter the input directory containing videos: /videos
Enter the output directory for extracted frames: /frames
Enter the desired frames per second (FPS): 5
Select the output image format:
1: jpg
2: jpeg
3: png
4: tif
Enter the format number: 1
```
3. The extracted frames will be saved in:
```
/frames
   ├── video1
   │   ├── frame_0000.jpg
   │   ├── frame_0001.jpg
   ├── video2
       ├── frame_0000.jpg
       ├── frame_0001.jpg
```

## Code Functionality
1. Reads video files from the input directory.
2. Extracts frames at the specified FPS.
3. Saves frames in the user-specified image format.
4. Uses `tqdm` to display a progress bar.
5. Handles both interactive and command-line executions.

## LICENSE
This project is licensed under the [MIT License](LICENSE).
