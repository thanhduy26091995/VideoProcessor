import json
import logging
import os
import shutil
import subprocess
import uuid

import firebase_admin
from firebase_admin import credentials, storage

# Firebase Admin SDK initialization
cred = credentials.Certificate("./firebase-service-account-key.json")
FIREBASE_STORAGE_BUCKET_NAME = "CHANGE YOUR STORAGE BUCKET HERE"

firebase_admin.initialize_app(cred, {
    'storageBucket': FIREBASE_STORAGE_BUCKET_NAME
})

# Configuration
THUMBNAIL_DIR = "../../outputs/thumbnails"
THUMBNAIL_INTERVAL = 1  # Interval in seconds to extract thumbnails
THUMBNAIL_SIZES = {
    "small": 320,
    "medium": 640
}
PREVIEW_TIMES = [(5, 10), (15, 20)]  # Time ranges for preview clips
LOG_FILE = "../../outputs/process_log.txt"
OUTPUT_FILE = "../../outputs/response.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # This will also output to console
    ]
)


def cleanup_files():
    if os.path.exists(THUMBNAIL_DIR):
        shutil.rmtree(THUMBNAIL_DIR)
    if os.path.exists("video.mp4"):
        os.remove("video.mp4")


def download_video(video_url):
    output_file = "video.mp4"
    logging.info(f"Downloading video from {video_url}...")
    subprocess.run(['ffmpeg', '-i', video_url, '-c', 'copy', output_file], check=True)
    logging.info(f"Downloaded video to {output_file}.")
    return output_file


def get_video_duration(video_file):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                             'default=noprint_wrappers=1:nokey=1', video_file],
                            stdout=subprocess.PIPE)
    duration = float(result.stdout.decode().strip())
    return duration


def get_video_dimensions(video_file):
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                             'stream=width,height', '-of', 'csv=s=x:p=0', video_file],
                            stdout=subprocess.PIPE)
    dimensions = result.stdout.decode().strip().split('x')
    width = int(dimensions[0])
    height = int(dimensions[1])
    return width, height


def calculate_thumbnail_size(video_width, video_height, thumbnail_size):
    aspect_ratio = video_width / video_height
    size = thumbnail_size
    if video_width > video_height:
        return (size, int(size / aspect_ratio))
    else:
        return (int(size * aspect_ratio), size)


def upload_to_firebase(local_file_path, firebase_path):
    bucket = storage.bucket()
    blob = bucket.blob(firebase_path)
    blob.upload_from_filename(local_file_path)
    blob.make_public()
    return blob.public_url


def generate_thumbnails(video_file, video_name):
    if not os.path.exists(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR)

    logging.info(f"Generating thumbnails for {video_file}...")
    thumbnails = {"small": [], "medium": []}
    video_width, video_height = get_video_dimensions(video_file)
    index = 0

    while True:
        timestamp = index * THUMBNAIL_INTERVAL
        processing_success = False

        for size_name, base_size in THUMBNAIL_SIZES.items():
            resolution = calculate_thumbnail_size(video_width, video_height, base_size)
            thumbnail_file = os.path.join(THUMBNAIL_DIR, f"{size_name}_thumbnail_{timestamp}.jpg")
            result = subprocess.run(
                ['ffmpeg', '-i', video_file, '-ss', str(timestamp), '-vframes', '1', '-s',
                 f"{resolution[0]}x{resolution[1]}", thumbnail_file],
                stderr=subprocess.PIPE
            )

            if result.returncode != 0 or not os.path.exists(thumbnail_file):
                logging.warning(f"Failed to generate {size_name} thumbnail at {timestamp}s.")
                continue

            processing_success = True
            firebase_path = f"thumbnails/{video_name}/{size_name}/thumbnail_{timestamp}.jpg"
            thumbnail_url = upload_to_firebase(thumbnail_file, firebase_path)
            thumbnails[size_name].append({
                "thumbnailUrl": thumbnail_url,
                "time": timestamp
            })

        if not processing_success:
            logging.info(f"No more thumbnails generated after {timestamp}s.")
            break

        index += 1

    logging.info(f"Generated thumbnails for timestamps up to {index * THUMBNAIL_INTERVAL} seconds.")
    return thumbnails


def generate_preview_clips(video_file, video_name):
    previews = []
    logging.info(f"Generating preview clips for {video_file}...")
    for start_time, end_time in PREVIEW_TIMES:
        preview_file = f"preview_{start_time}_{end_time}.mp4"
        result = subprocess.run(
            ['ffmpeg', '-i', video_file, '-ss', str(start_time), '-to', str(end_time), '-c', 'copy', preview_file],
            stderr=subprocess.PIPE
        )

        if result.returncode != 0 or not os.path.exists(preview_file):
            logging.warning(f"Failed to generate preview clip from {start_time}s to {end_time}s.")
            continue

        firebase_path = f"previews/{video_name}/{preview_file}"
        preview_url = upload_to_firebase(preview_file, firebase_path)
        previews.append({
            "url": preview_url,
            "start_time": start_time * 1000,  # Convert to milliseconds
            "end_time": end_time * 1000
        })

    logging.info(f"Generated {len(previews)} preview clips.")
    return previews


def process_video(video_info):
    cleanup_files()
    video_file = download_video(video_info['url'])
    video_name = os.path.splitext(os.path.basename(video_info['url']))[0]

    duration = get_video_duration(video_file)
    if duration < 10:
        logging.info(f"Skipping thumbnail generation for {video_file}. Duration is less than 10 seconds.")
        return None

    thumbnails = generate_thumbnails(video_file, video_name)
    previews = generate_preview_clips(video_file, video_name) if video_info['url'].endswith(('.hls', '.dash')) else []

    video_metadata = {
        "status": "success",
        "video_id": str(uuid.uuid4()),  # Generate a unique video ID
        "processing_status": "completed",
        "video_url": upload_to_firebase(video_file, f"videos/{video_name}.mp4"),
        "metadata": {
            "duration": int(duration * 1000),  # Convert to milliseconds
            "width": video_info['width'],
            "height": video_info['height'],
            "bitrate": f"{int(video_info['bitrate'])}kbps",
            "codec": "H.264"
        },
        "thumbnails": thumbnails,
        "previews": previews
    }

    return video_metadata


if __name__ == "__main__":
    videos = [
        {
            "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/1_20240812063339_5927708-hd_1080_1920_30fps.mp4",
            "bitrate": 4698.624,
            "width": 1080.0,
            "height": 1920.0
        }
    ]

    results = []
    for video in videos:
        result = process_video(video)
        if result is not None:
            results.append(result)

    # Save the results to a .json file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=4)

    logging.info(f"Processing completed. Results saved to {OUTPUT_FILE}")
