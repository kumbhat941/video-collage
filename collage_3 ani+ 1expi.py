import os
import subprocess
from pathlib import Path

# Define paths
experiment_video = r"D:\HTO\Batch_Melting\20250128_Mit_fining_agent_Double_Weights\Mit_Fining_Agent.mp4"
animation_folder = r"D:\HTO\Batch_Melting\20250128_Mit_fining_agent_Double_Weights\Gas_Presentation"
output_video = r"D:\HTO\Batch_Melting\20250128_Mit_fining_agent_Double_Weights\output_collage.mp4"

# Get all MP4 animation videos in the folder
animation_videos = [str(f) for f in Path(animation_folder).glob("*.mp4")]

# Ensure there are at least 3 animation videos
if len(animation_videos) < 3:
    print("Not enough animation videos! At least 3 required. Exiting...")
    exit()

# Resize the experiment video to 1280x720 (left side)
experiment_video_resized = experiment_video.replace(".mp4", "_resized.mp4")
subprocess.run([
    "ffmpeg", "-i", experiment_video, "-vf", "scale=1280:720", "-c:v", "libx264",
    "-preset", "slow", "-crf", "18", "-b:v", "5000k", experiment_video_resized, "-y"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Resize animation videos to 640x240 (right side, stacked)
resized_videos = []
for i, video in enumerate(animation_videos[:3]):  # Limit to 3 animations
    resized_video = video.replace(".mp4", "_resized.mp4")
    subprocess.run([
        "ffmpeg", "-i", video, "-vf", "scale=640:240", "-c:v", "libx264",
        "-preset", "slow", "-crf", "18", "-b:v", "5000k", resized_video, "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    resized_videos.append(resized_video)

# FFmpeg filter_complex to position videos correctly
filter_complex = (
    "[1:v][2:v]vstack=inputs=2[top];"  # Stack animation 1 & 2
    "[top][3:v]vstack=inputs=2[right];"  # Add animation 3 below them
    "[0:v][right]hstack=inputs=2"  # Combine with experiment video on the left
)

# Build FFmpeg command
ffmpeg_command = ["ffmpeg", "-i", experiment_video_resized]
for video in resized_videos:
    ffmpeg_command.extend(["-i", video])
ffmpeg_command.extend([
    "-filter_complex", filter_complex,
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-b:v", "5000k",
    output_video, "-y"
])

# Run FFmpeg to merge videos
print("Merging videos into high-quality collage...")
subprocess.run(ffmpeg_command)

# Clean up resized videos
os.remove(experiment_video_resized)
for video in resized_videos:
    os.remove(video)

print(f"✅ High-quality collage video saved at: {output_video}")
