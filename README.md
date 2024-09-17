# Video Processing Project

This project provides tools to generate thumbnails, calculate video ratios, and upload videos to Firebase Storage. Follow the instructions below to set up and use the scripts.
Also it use for practice Python

## Setup

1. Place your `firebase-service-account-key.json` file at the root folder of this project.
2. Update the `FIREBASE_STORAGE_BUCKET_NAME` variable in your scripts to reflect your Firebase storage bucket name:

   ```python
   FIREBASE_STORAGE_BUCKET_NAME = "CHANGE YOUR STORAGE BUCKET HERE"
   ```

## Scripts Overview

### 1. `generate_thumbnail.py`
- **Description:** This script generates thumbnails for a video.
- **Configuration:** You can configure `THUMBNAIL_INTERVAL` to set the interval between thumbnails and `THUMBNAIL_SIZES` to define the sizes of the thumbnails.
- **Usage:** Provide the `VIDEO_URL` as input to generate the thumbnails.

### 2. `process_video.py`
- **Description:** This script combines various operations, including thumbnail generation and ratio calculation, and produces a `.json` response file.
- **Input:** A list of video dictionaries, each containing:
  - `url`: Video URL
  - `bitrate`: Bitrate of the video
  - `width`: Width of the video
  - `height`: Height of the video
- **Example Input:**

   ```python
   videos = [
       {
           "url": "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/1_20240812063339_5927708-hd_1080_1920_30fps.mp4",
           "bitrate": 4698.624,
           "width": 1080.0,
           "height": 1920.0
       }
   ]
   ```

### 3. `ratio_calculation.py`
- **Description:** This script calculates the aspect ratio of the video.

### 4. `upload_video.py`
- **Description:** This script downloads a video from the provided URL and uploads it back to the configured Firebase Storage bucket.

## How to Generate a Custom Response

To create your own response `.json` file, follow these steps:

1. Run `upload_video.py` to upload the video to Firebase Storage.
2. Run `ratio_calculation.py` to calculate the aspect ratio of the video.
3. Run `process_video.py` to generate the final response `.json` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
