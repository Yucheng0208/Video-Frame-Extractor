import os
import cv2
import argparse
from tqdm import tqdm

def extract_frames_from_videos(input_dir, output_dir, fps, img_format):
    try:
        if not output_dir:
            output_dir = input_dir

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        if not video_files:
            print("No video files found in the selected directory.")
            return

        for video_file in video_files:
            video_path = os.path.join(input_dir, video_file)
            video_name, _ = os.path.splitext(video_file)
            video_output_dir = os.path.join(output_dir, video_name)
            os.makedirs(video_output_dir, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            original_fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_interval = max(1, original_fps // fps)
            frame_count = 0
            extracted_count = 0

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            with tqdm(total=total_frames, desc=f"Processing {video_file}", unit="frame") as pbar:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % frame_interval == 0:
                        frame_filename = os.path.join(video_output_dir, f"frame_{extracted_count:04d}.{img_format}")
                        cv2.imwrite(frame_filename, frame)
                        extracted_count += 1

                    frame_count += 1
                    pbar.update(1)

            cap.release()
        print("Frames extracted successfully!")
    except Exception as e:
        print(f"Failed to extract frames: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract frames from videos.")
    parser.add_argument("--input_dir", type=str, required=False, help="Input directory containing videos.")
    parser.add_argument("--output_dir", type=str, required=False, help="Output directory for extracted frames.")
    parser.add_argument("--fps", type=int, required=False, help="Desired frames per second (FPS).")
    parser.add_argument("--img_format", type=str, choices=["jpg", "jpeg", "png", "tif"], required=False, help="Output image format.")
    
    args = parser.parse_args()
    
    if args.input_dir and args.output_dir and args.fps and args.img_format:
        extract_frames_from_videos(args.input_dir, args.output_dir, args.fps, args.img_format)
    else:
        input_dir = input("Enter the input directory containing videos: ").strip()
        output_dir = input("Enter the output directory for extracted frames: ").strip()
        fps = int(input("Enter the desired frames per second (FPS): ").strip())
        
        format_options = {"1": "jpg", "2": "jpeg", "3": "png", "4": "tif"}
        print("Select the output image format:")
        for key, value in format_options.items():
            print(f"{key}: {value}")
        
        format_choice = input("Enter the format number: ").strip()
        img_format = format_options.get(format_choice, "png")  # 預設為 png
        
        if not os.path.isdir(input_dir):
            print("Invalid input directory.")
        else:
            extract_frames_from_videos(input_dir, output_dir, fps, img_format)
