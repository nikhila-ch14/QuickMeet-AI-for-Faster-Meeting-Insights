import os
import requests
import time
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

def generate_video(summary_text, output_path="static/meeting_summary.mp4"):
    """
    Generate a video using HeyGen API where the AI avatar reads the meeting summary.
    """
    url = "https://api.heygen.com/v1/video/generate"
    
    headers = {
        "Authorization": f"Bearer {HEYGEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "video_config": {
            "source": "text",
            "text": summary_text,  # Text that the avatar will read
            "voice_id": "en_us_001",  # Change this to your preferred voice
            "avatar_id": "0cf2ce04c1a04c54979cbe3373def2ec",  # Your AI avatar ID
            "resolution": "720p",
            "background": "white",
            "motion": True  # Ensure avatar has motion
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        video_id = response_data.get("video_id")
        
        # Check video status and download once completed
        video_url = check_video_status(video_id)
        
        if video_url:
            download_video(video_url, output_path)
            return output_path
        else:
            raise Exception("Failed to get video URL.")
    else:
        raise Exception(f"Failed to generate video: {response.text}")

def check_video_status(video_id):
    """
    Check the status of the generated video.
    """
    url = f"https://api.heygen.com/v1/video/status/{video_id}"
    
    headers = {
        "Authorization": f"Bearer {HEYGEN_API_KEY}"
    }
    
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get("status")
            
            if status == "completed":
                return status_data.get("video_url")  # Return the final video URL
            elif status == "failed":
                raise Exception("Video generation failed.")
            else:
                print(f"Video is still processing... ({status})")
                time.sleep(10)  # Wait and check again
        else:
            raise Exception(f"Failed to check video status: {response.text}")

def download_video(video_url, output_path):
    """
    Download the video from HeyGen and save it to the static/ folder.
    """
    # Ensure "static" directory exists
    if not os.path.exists("static"):
        os.makedirs("static")

    response = requests.get(video_url, stream=True)
    
    if response.status_code == 200:
        with open(output_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=1024):
                video_file.write(chunk)
        print(f"Video downloaded successfully: {output_path}")
    else:
        raise Exception(f"Failed to download video: {response.status_code}")
