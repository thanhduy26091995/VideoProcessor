import json

import ffmpeg


class MediaInfo:
    def __init__(self, url, bitrate, width, height):
        self.url = url
        self.bitrate = bitrate
        self.width = width
        self.height = height

    def to_dict(self):
        return {
            "url": self.url,
            "bitrate": self.bitrate,
            "width": self.width,
            "height": self.height
        }


def get_video_info_from_url(url):
    """Get video information (bitrate, width, height) from a video URL."""
    try:
        probe = ffmpeg.probe(url)
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')

        width = float(video_stream['width'])
        height = float(video_stream['height'])
        bitrate = float(video_stream.get('bit_rate', 0)) / 1000  # Convert bitrate to kbps

        return MediaInfo(url, bitrate, width, height)
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None


def generate_json_list(url_list):
    media_info_list = []

    for url in url_list:
        info = get_video_info_from_url(url)
        if info:
            media_info_list.append(info.to_dict())

    json_list = json.dumps(media_info_list, indent=4)
    return json_list


# Example usage
url_list = [
    "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/1_20240812063339_5927708-hd_1080_1920_30fps.mp4"
]

json_data = generate_json_list(url_list)
print(json_data)
