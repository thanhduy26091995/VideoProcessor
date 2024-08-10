#!/bin/bash

# Define the input in a format similar to your Kotlin code
input='
    val urlList = listOf(
        MediaInfo(
            url = "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_1.mp4",
            bitrate = 413.979,
            width = 480.0,
            height = 360.0
        ),
        MediaInfo(
            url = "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_3.mp4",
            bitrate = 4848.262,
            width = 1080.0,
            height = 1920.0
        ),
        MediaInfo(
            url = "https://storage.googleapis.com/smoothscroll-7252a.appspot.com/videos/video_4.mp4",
            bitrate = 9609.989,
            width = 2560.0,
            height = 1440.0
        )
    )
'

# Print the input for debugging
echo "Input data:"
echo "$input"

# Function to convert the input format to JSON
convert_to_json() {
    # Clean input and prepare for JSON conversion
    echo "$input" | \
    sed -n -e 's/.*url = "\(https:\/\/[^\"]*\)",\s*bitrate = \([0-9.]*\),\s*width = \([0-9.]*\),\s*height = \([0-9.]*\).*/{"url": "\1", "bitrate": \2, "width": \3, "height": \4}/p' | \
    awk 'BEGIN {print "["} {if (NR>1) {printf ","} print $0} END {print "]"}'
}

# Execute the function and output the JSON string
json_output=$(convert_to_json)

# Print the JSON output for debugging
echo "JSON output:"
echo "$json_output"

# Check if JSON output is empty and print a message if it is
if [ -z "$json_output" ]; then
    echo "Error: JSON output is empty. Please check the input format."
fi
