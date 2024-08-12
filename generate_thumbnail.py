import os
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import shutil

# Configuration
VIDEO_URL = "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/1_20240812063339_5927708-hd_1080_1920_30fps.mp4"
THUMBNAIL_DIR = "thumbnails"
THUMBNAIL_INTERVAL = 1  # Interval in seconds to extract thumbnails
PORT = 8000  # Port for the HTTP server
THUMBNAIL_SIZES = {
    "small": "320x240",
    "medium": "640x480"
}

def cleanup_files():
    # Remove existing thumbnail directory and its contents
    if os.path.exists(THUMBNAIL_DIR):
        shutil.rmtree(THUMBNAIL_DIR)

    # Remove existing video file
    if os.path.exists("video.mp4"):
        os.remove("video.mp4")

def download_video(video_url):
    # Use ffmpeg to download the video
    output_file = "video.mp4"
    subprocess.run(['ffmpeg', '-i', video_url, '-c', 'copy', output_file], check=True)
    return output_file

def generate_thumbnails(video_file):
    if not os.path.exists(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR)

    thumbnails = {"thumbnail": {"small": [], "medium": {}}}
    index = 0
    while True:
        timestamp = index * THUMBNAIL_INTERVAL
        thumbnail_data = {"small": [], "medium": {}}
        for size_name, resolution in THUMBNAIL_SIZES.items():
            thumbnail_file = os.path.join(THUMBNAIL_DIR, f"{size_name}_thumbnail_{timestamp}.jpg")
            result = subprocess.run(
                ['ffmpeg', '-i', video_file, '-ss', str(timestamp), '-vframes', '1', '-s', resolution, thumbnail_file],
                stderr=subprocess.PIPE
            )

            # Break if ffmpeg fails or thumbnail is not created
            if result.returncode != 0 or not os.path.exists(thumbnail_file):
                break

            if size_name == "small":
                thumbnail_data["small"].append({
                    "thumbnailUrl": f"http://localhost:{PORT}/{os.path.basename(thumbnail_file)}",
                    "duration": timestamp
                })
            elif size_name == "medium":
                thumbnail_data["medium"] = {
                    "thumbnailUrl": f"http://localhost:{PORT}/{os.path.basename(thumbnail_file)}",
                    "duration": timestamp
                }

        if not thumbnail_data["small"] and not thumbnail_data["medium"]:
            break
        
        thumbnails["thumbnail"]["small"].extend(thumbnail_data["small"])
        thumbnails["thumbnail"]["medium"] = thumbnail_data["medium"]
        index += 1

    return thumbnails

def run_http_server(directory, port):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', port), handler)
    print(f"Serving at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Clean up old files and directories
    cleanup_files()

    # Download the video
    video_file = download_video(VIDEO_URL)

    # Generate thumbnails
    thumbnails = generate_thumbnails(video_file)

    # Print the thumbnail metadata
    print("Thumbnail metadata:")
    print(json.dumps(thumbnails, indent=4))

    # Start the HTTP server to serve thumbnails
    run_http_server(THUMBNAIL_DIR, PORT)
