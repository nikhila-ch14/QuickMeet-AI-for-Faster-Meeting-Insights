import os
import requests
import time
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

# Configurable parameters
VOICE_ID = "1bd001e7e50f421d891986aad5158bc8"  # Replace with your selected voice_id from HeyGen
AVATAR_ID = "fc860c2705d244c787e8ea0188bc4c97"          # Replace with your selected avatar_id from HeyGen

def read_input_files():
    """
    Reads the content of summary.txt and action_items.txt and returns the concatenated text.
    """
    summary_file = "summary.txt"
    action_items_file = "action_items.txt"
    
    if not os.path.exists(summary_file):
        raise FileNotFoundError(f"File not found: {summary_file}")
    if not os.path.exists(action_items_file):
        raise FileNotFoundError(f"File not found: {action_items_file}")
    
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_text = f.read().strip()
        
    with open(action_items_file, "r", encoding="utf-8") as f:
        action_items_text = f.read().strip()
        
    # Combine the two texts with a newline separator.
    combined_text = f"{summary_text}\n\n{action_items_text}"
    
    # Warn if text might be too long (over 1500 characters)
    if len(combined_text) > 1500:
        print("Warning: The combined text is over 1500 characters. HeyGen API requires text input to be less than 1500 characters.")
    
    return combined_text

def generate_video(text, output_path="static/meeting_summary.mp4"):
    """
    Generate a video using the HeyGen API where the AI avatar reads the given text.
    """
    url = "https://api.heygen.com/v2/video/generate"
    
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": AVATAR_ID,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": text,
                    "voice_id": VOICE_ID,
                    "speed": 1.0
                }
            }
        ],
        "dimension": {
            "width": 1280,
            "height": 720
        }
    }
    
    print("Sending video generation request...")
    response = requests.post(url, json=payload, headers=headers)
    
    try:
        response_data = response.json()
    except Exception as e:
        raise Exception("Failed to decode response JSON: " + str(e))
    
    print("Response data:", response_data)
    
    # Corrected video_id extraction
    video_id = response_data.get("data", {}).get("video_id")
    if not video_id:
        raise Exception("Video generation did not return a valid video_id.")
    
    print(f"Video generation started with video_id: {video_id}")
    
    # Check video status and download once completed
    video_url = check_video_status(video_id)
    if video_url:
        download_video(video_url, output_path)
        return output_path
    else:
        raise Exception("Failed to retrieve video URL after generation.")

def check_video_status(video_id):
    """
    Poll the HeyGen API for the status of the generated video.
    """
    url = f"https://api.heygen.com/v2/video/status?video_id={video_id}"
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Accept": "application/json"
    }
    
    while True:
        print("Checking video status...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error: Received status code {response.status_code} from HeyGen API")

        try:
            status_data = response.json()
        except Exception as e:
            print("Error: Empty or invalid JSON response from HeyGen API.")
            print("Raw response:", response.text)
            raise Exception("Failed to decode status response JSON: " + str(e))
        
        print("Status data:", status_data)

        if "data" not in status_data:
            raise Exception("Error: 'data' key missing in HeyGen response.")

        status = status_data["data"].get("status")
        print(f"Current video status: {status}")

        if status == "completed":
            return status_data["data"].get("video_url")
        elif status == "failed":
            raise Exception("Video generation failed.")
        else:
            time.sleep(10)  # Wait and check again after 10 seconds

def download_video(video_url, output_path):
    """
    Download the video from HeyGen and save it to the specified path.
    """
    directory = os.path.dirname(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    
    print(f"Downloading video from: {video_url}")
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    video_file.write(chunk)
        print(f"Video downloaded successfully: {output_path}")
    else:
        raise Exception(f"Failed to download video: {response.status_code}")

if __name__ == "__main__":

    try:
        # Read and combine text from input files
        text_to_read = read_input_files()
        print("Input text successfully read from summary.txt and action_items.txt.")
        
        # Generate the video with the combined text
        video_path = generate_video(text_to_read)
        print(f"Video generated and saved at: {video_path}")
    except Exception as e:
        print(f"An error occurred: {e}")