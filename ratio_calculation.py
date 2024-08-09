import os
import ffmpeg

class MediaInfo:
    def __init__(self, url, bitrate, width, height):
        self.url = url
        self.bitrate = bitrate
        self.width = width
        self.height = height

    def __str__(self):
        return f'MediaInfo(url: "{self.url}", bitrate: {self.bitrate}, width: {self.width}, height: {self.height})'

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

def generate_kotlin_val(url_list):
    media_info_list = []
    
    for url in url_list:
        info = get_video_info_from_url(url)
        if info:
            media_info_list.append(str(info))
    
    kotlin_val = f"val urlList = listOf(\n    {',\n    '.join(media_info_list)}\n)"
    return kotlin_val

# Example usage
url_list = [
   "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_1.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_3.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_4.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_5.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_6.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_7.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_8.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_9.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_10.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_11.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_12.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_13.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_14.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_15.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_16.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_17.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_18.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_19.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_20.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_21.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_22.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_23.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_24.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_25.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_26.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_27.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_28.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_29.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_30.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_31.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_32.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_33.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_34.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_35.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_36.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_37.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_38.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_39.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_40.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_41.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_42.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/1_20240808181704_5512609-hd_1080_1920_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/2_20240808181708_9861969-uhd_1440_2732_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/3_20240808181711_8045175-hd_1080_1920_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/4_20240808181713_7414127-hd_1920_1080_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/5_20240808181715_8032945-uhd_1440_2560_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/6_20240808181718_7515918-hd_1080_1920_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/7_20240808181721_5992585-uhd_1440_2560_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/8_20240808181724_8045109-hd_1080_1920_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/9_20240808181728_6077718-uhd_2560_1440_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/10_20240808181733_7612773-hd_1080_1920_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/11_20240808181737_7322355-uhd_1440_2732_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/12_20240808181744_5642526-hd_1080_1920_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/13_20240808181753_7181824-uhd_1440_2732_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/14_20240808181817_2169880-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/15_20240808181831_3015510-hd_1920_1080_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/16_20240808181834_3135808-hd_1920_1080_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/17_20240808181836_2252797-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/18_20240808181841_2519660-uhd_2560_1440_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/19_20240808181847_3018669-hd_1920_1080_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/20_20240808181851_3629511-hd_720_900_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/21_20240808181859_2053855-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/22_20240808181911_1854202-hd_1280_720_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/23_20240808181921_2249630-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/24_20240808181928_2867873-uhd_2560_1440_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/25_20240808181934_3015527-hd_1920_1080_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/26_20240808181941_2711092-uhd_2560_1440_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/27_20240808181946_3775278-hd_1920_1080_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/28_20240808181951_3120159-uhd_2560_1440_25fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/29_20240808182103_2146396-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/30_20240808182114_2103099-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/31_20240808182131_2933375-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/32_20240808182142_2547258-uhd_2560_1440_30fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/33_20240808182147_3059073-hd_1920_1080_24fps.mp4",
        "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/34_20240808182151_1994829-hd_1920_1080_24fps.mp4"
]

kotlin_code = generate_kotlin_val(url_list)
print(kotlin_code)
