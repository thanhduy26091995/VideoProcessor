import json

import requests

url = "https://firebasestorage.googleapis.com/v0/b/smoothscroll-7252a.appspot.com/o/video_list.json?alt=media&token=77339fd9-3ad3-44f0-9aa4-b529f91c1c36"

response = requests.get(url)

if response.status_code == 200:
    # Parse the JSON content
    json_content = response.json()  # Equivalent to json.loads(response.content)

    # Format the JSON content with indentation
    formatted_json = json.dumps(json_content, indent=4)

    # Print the formatted JSON
    print(formatted_json)
else:
    print("Failed to retrieve data. Status code:", response.status_code)
