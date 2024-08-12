import os
import requests
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime
# Path to your Firebase service account key JSON file
SERVICE_ACCOUNT_KEY_PATH = "./firebase-service-account-key.json"

# Firebase Storage bucket name
FIREBASE_STORAGE_BUCKET_NAME = "smoothscroll-7252a.appspot.com"

def initialize_firebase():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH)
    client = storage.Client(credentials=credentials, project=credentials.project_id)
    return client.bucket(FIREBASE_STORAGE_BUCKET_NAME)

def download_video(url, output_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Ensure we notice bad responses
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    except requests.exceptions.HTTPError as err:
        print(f"Failed to download {url}: {err}")
        return False
    return True

def file_exists(bucket, remote_file_name):
    blob = bucket.blob(remote_file_name)
    return blob.exists()

def generate_timestamped_file_name(url, index):
    # Generate a timestamped file name based on the current time
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    base_name = os.path.basename(url)
    return f"videos/{index}_{timestamp}_{base_name}"

def upload_video_to_firebase(bucket, local_file_path, remote_file_name):
    if file_exists(bucket, remote_file_name):
        print(f"File already exists: {remote_file_name}")
        return bucket.blob(remote_file_name).public_url

    blob = bucket.blob(remote_file_name)
    blob.upload_from_filename(local_file_path)
    blob.make_public()
    return blob.public_url

def process_videos(url_list):
    bucket = initialize_firebase()
    uploaded_urls = []

    for idx, video_url in enumerate(url_list):
        print(f"Processing video {idx + 1}/{len(url_list)}: {video_url}")

        # Download video
        local_file_name = f"video_{idx + 1}.mp4"
        if not download_video(video_url, local_file_name):
            continue

        # Generate timestamped remote file name
        remote_file_name = generate_timestamped_file_name(video_url, idx + 1)
        
        # Upload to Firebase if not already uploaded
        uploaded_url = upload_video_to_firebase(bucket, local_file_name, remote_file_name)
        uploaded_urls.append(uploaded_url)

        # Clean up the local file
        os.remove(local_file_name)

    return uploaded_urls

if __name__ == "__main__":
    # Input list of video URLs
    url_list = [
        "https://videos.pexels.com/video-files/5927708/5927708-hd_1080_1920_30fps.mp4"
    ]

    uploaded_video_urls = process_videos(url_list)

    # Format the result to match the input format
    formatted_urls = "        " + ",\n        ".join(f'"{url}"' for url in uploaded_video_urls)
    result = f"private val urlList = listOf(\n{formatted_urls}\n    )"
    
    # Print or save the result
    print(result)