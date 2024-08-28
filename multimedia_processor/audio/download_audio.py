import json
import os

import firebase_admin
import yt_dlp
from firebase_admin import credentials, storage


# Load configuration from config.json
def load_config(config_file='config.json'):
    with open(config_file, 'r') as file:
        return json.load(file)


config = load_config()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(config['SERVICE_ACCOUNT_KEY_PATH'])
FIREBASE_STORAGE_BUCKET_NAME = config['FIREBASE_STORAGE_BUCKET_NAME']

firebase_admin.initialize_app(cred, {
    'storageBucket': FIREBASE_STORAGE_BUCKET_NAME
})


def upload_to_firebase(local_file_path, firebase_path):
    bucket = storage.bucket()

    # Create new blob then upload the file
    blob = bucket.blob(firebase_path)
    blob.upload_from_filename(local_file_path)

    # Make the blob publicly accessible
    blob.make_public()

    # Get the URL of the uploaded file
    return blob.public_url


def download_audio(urls, output_path='outputs/audios', metadata_file='outputs/audio_metadata.json'):
    """Function download audio base on url list."""

    metadata_list = []

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                # Extract metadata
                info_dict = ydl.extract_info(url, download=False)

                # Download audio
                ydl.download([url])

                # Extract detail metadata
                music_name = info_dict.get('title', 'Unknown title')
                artist = info_dict.get(
                    'artist', info_dict.get('uploader', 'Unknown artist'))
                duration = info_dict.get('duration', 0)
                thumbnail_url = info_dict.get('thumbnail', 'No thumbnail')

                # Define the local file path
                local_file_path = os.path.join(output_path, f"{music_name}.mp3")

                # Upload the audio to Firebase Storage
                audio_url = upload_to_firebase(local_file_path, f"audios/{music_name}.mp3")

                # Create the metadata dictionary
                metadata = {
                    "audioUrl": audio_url,
                    "name": music_name,
                    "artist": artist,
                    "duration": duration,
                    "thumbnailUrl": thumbnail_url,
                    "source": url
                }
                # Append the metadata to the list
                metadata_list.append(metadata)

            except Exception as e:
                print(f"An error occurred with {url}: {e}")

    # Save metadata to a JSON file
    with open(metadata_file, 'w', encoding='utf-8') as json_file:
        json.dump(metadata_list, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    youtube_urls = [
        "https://www.youtube.com/watch?v=YQHsXMglC9A",
        "https://www.youtube.com/watch?v=mHONNcZbwDY",
        "https://www.youtube.com/watch?v=HzjE33U_gy8",
    ]
    download_audio(youtube_urls)
