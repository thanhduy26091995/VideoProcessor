import os
import subprocess
import json
import shutil
import uuid
import logging
import firebase_admin
from firebase_admin import credentials, storage

# Firebase Admin SDK initialization
cred = credentials.Certificate("./firebase-service-account-key.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'smoothscroll-7252a.appspot.com'
})

# Configuration
THUMBNAIL_DIR = "thumbnails"
THUMBNAIL_INTERVAL = 1  # Interval in seconds to extract thumbnails
THUMBNAIL_SIZES = {
    "small": 320,
    "medium": 640
}
PREVIEW_TIMES = [(5, 10), (15, 20)]  # Time ranges for preview clips
LOG_FILE = "process_log.txt"
OUTPUT_FILE = "response.json"

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
                ['ffmpeg', '-i', video_file, '-ss', str(timestamp), '-vframes', '1', '-s', f"{resolution[0]}x{resolution[1]}", thumbnail_file],
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
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_1.mp4",
        "bitrate": 413.979,
        "width": 480.0,
        "height": 360.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_3.mp4",
        "bitrate": 4848.262,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_4.mp4",
        "bitrate": 9609.989,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_12.mp4",
        "bitrate": 4214.07,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_13.mp4",
        "bitrate": 11949.588,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_14.mp4",
        "bitrate": 6748.882,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_15.mp4",
        "bitrate": 13567.945,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_16.mp4",
        "bitrate": 5038.343,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_17.mp4",
        "bitrate": 3102.623,
        "width": 1366.0,
        "height": 720.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_18.mp4",
        "bitrate": 6050.07,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_19.mp4",
        "bitrate": 9204.764,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_20.mp4",
        "bitrate": 21337.469,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_21.mp4",
        "bitrate": 3732.412,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_22.mp4",
        "bitrate": 4895.006,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_23.mp4",
        "bitrate": 4997.132,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_24.mp4",
        "bitrate": 4970.552,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_25.mp4",
        "bitrate": 5191.702,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_26.mp4",
        "bitrate": 2826.667,
        "width": 1280.0,
        "height": 720.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_27.mp4",
        "bitrate": 5466.637,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_28.mp4",
        "bitrate": 2491.824,
        "width": 1280.0,
        "height": 720.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_29.mp4",
        "bitrate": 5583.877,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_30.mp4",
        "bitrate": 12126.331,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_31.mp4",
        "bitrate": 5569.103,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_32.mp4",
        "bitrate": 11908.217,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_33.mp4",
        "bitrate": 5087.127,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_34.mp4",
        "bitrate": 5365.035,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_35.mp4",
        "bitrate": 4861.016,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_36.mp4",
        "bitrate": 4838.884,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_37.mp4",
        "bitrate": 4309.063,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_38.mp4",
        "bitrate": 12853.113,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_39.mp4",
        "bitrate": 4161.274,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_40.mp4",
        "bitrate": 4973.189,
        "width": 1440.0,
        "height": 2732.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_41.mp4",
        "bitrate": 6509.912,
        "width": 1440.0,
        "height": 2732.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_42.mp4",
        "bitrate": 13151.886,
        "width": 1440.0,
        "height": 2732.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/1_20240808181704_5512609-hd_1080_1920_25fps.mp4",
        "bitrate": 3465.883,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/2_20240808181708_9861969-uhd_1440_2732_25fps.mp4",
        "bitrate": 5143.8,
        "width": 1440.0,
        "height": 2732.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/3_20240808181711_8045175-hd_1080_1920_25fps.mp4",
        "bitrate": 4654.184,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/4_20240808181713_7414127-hd_1920_1080_24fps.mp4",
        "bitrate": 4893.314,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/5_20240808181715_8032945-uhd_1440_2560_24fps.mp4",
        "bitrate": 5966.324,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/6_20240808181718_7515918-hd_1080_1920_30fps.mp4",
        "bitrate": 3834.777,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/7_20240808181721_5992585-uhd_1440_2560_25fps.mp4",
        "bitrate": 2976.572,
        "width": 1440.0,
        "height": 2560.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/8_20240808181724_8045109-hd_1080_1920_25fps.mp4",
        "bitrate": 3410.274,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/9_20240808181728_6077718-uhd_2560_1440_25fps.mp4",
        "bitrate": 12403.435,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/10_20240808181733_7612773-hd_1080_1920_25fps.mp4",
        "bitrate": 3637.577,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/11_20240808181737_7322355-uhd_1440_2732_25fps.mp4",
        "bitrate": 3376.366,
        "width": 1440.0,
        "height": 2732.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/12_20240808181744_5642526-hd_1080_1920_25fps.mp4",
        "bitrate": 5567.047,
        "width": 1080.0,
        "height": 1920.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/13_20240808181753_7181824-uhd_1440_2732_25fps.mp4",
        "bitrate": 7607.15,
        "width": 1440.0,
        "height": 2732.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/14_20240808181817_2169880-uhd_2560_1440_30fps.mp4",
        "bitrate": 13279.298,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/15_20240808181831_3015510-hd_1920_1080_24fps.mp4",
        "bitrate": 2321.889,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/16_20240808181834_3135808-hd_1920_1080_24fps.mp4",
        "bitrate": 4983.835,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/17_20240808181836_2252797-uhd_2560_1440_30fps.mp4",
        "bitrate": 5237.561,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/18_20240808181841_2519660-uhd_2560_1440_24fps.mp4",
        "bitrate": 11944.167,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/19_20240808181847_3018669-hd_1920_1080_24fps.mp4",
        "bitrate": 4876.624,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/20_20240808181851_3629511-hd_720_900_24fps.mp4",
        "bitrate": 2713.845,
        "width": 720.0,
        "height": 900.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/21_20240808181859_2053855-uhd_2560_1440_30fps.mp4",
        "bitrate": 13425.702,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/22_20240808181911_1854202-hd_1280_720_25fps.mp4",
        "bitrate": 2767.337,
        "width": 1280.0,
        "height": 720.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/23_20240808181921_2249630-uhd_2560_1440_30fps.mp4",
        "bitrate": 13735.295,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/24_20240808181928_2867873-uhd_2560_1440_24fps.mp4",
        "bitrate": 13666.468,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/25_20240808181934_3015527-hd_1920_1080_24fps.mp4",
        "bitrate": 5705.717,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/26_20240808181941_2711092-uhd_2560_1440_24fps.mp4",
        "bitrate": 13710.843,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/27_20240808181946_3775278-hd_1920_1080_25fps.mp4",
        "bitrate": 5145.978,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/28_20240808181951_3120159-uhd_2560_1440_25fps.mp4",
        "bitrate": 7863.286,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/29_20240808182103_2146396-uhd_2560_1440_30fps.mp4",
        "bitrate": 11626.309,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/30_20240808182114_2103099-uhd_2560_1440_30fps.mp4",
        "bitrate": 13374.464,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/31_20240808182131_2933375-uhd_2560_1440_30fps.mp4",
        "bitrate": 13156.701,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/32_20240808182142_2547258-uhd_2560_1440_30fps.mp4",
        "bitrate": 7662.604,
        "width": 2560.0,
        "height": 1440.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/33_20240808182147_3059073-hd_1920_1080_24fps.mp4",
        "bitrate": 5734.365,
        "width": 1920.0,
        "height": 1080.0
    },
    {
        "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/34_20240808182151_1994829-hd_1920_1080_24fps.mp4",
        "bitrate": 5241.299,
        "width": 1920.0,
        "height": 1080.0
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

