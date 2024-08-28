import subprocess
import ffmpeg
import os

# Configuration
mpd_url = "https://storage.googleapis.com/wvmedia/cenc/h264/tears/tears.mpd"
drm_license_url = "https://proxy.uat.widevine.com/proxy?video_id=GTS_SW_SECURE_CRYPTO&provider=widevine_test"
start_time = 10
end_time = 20
output_file = "preview.mp4"
decrypted_file = "decrypted.mp4"

# Step 1: Decrypt the video using Shaka Packager
packager_command = [
    "packager",
    f"input={mpd_url},stream=video,output={decrypted_file}",
    f"--enable_raw_key_decryption",
    f"--license_server_url={drm_license_url}"
]

# Run the Shaka Packager command
result = subprocess.run(packager_command, text=True, capture_output=True)

# Check if the decryption was successful
if result.returncode != 0:
    print(f"Error in Shaka Packager: {result.stderr}")
    exit(1)

# Ensure the decrypted file exists
if not os.path.exists(decrypted_file):
    print(f"Decryption failed: {decrypted_file} not found.")
    exit(1)

# Step 2: Trim the decrypted video using ffmpeg
ffmpeg.input(decrypted_file, ss=start_time, t=end_time - start_time).output(output_file).run()

print(f"Preview saved to {output_file}")
