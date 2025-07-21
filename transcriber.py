# quickmeet-backend/transcriber.py
import boto3
import time
import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# AWS Configuration
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "quickmeet-files")

# AWS Clients
transcribe = boto3.client("transcribe", region_name=REGION)
s3 = boto3.client("s3")

def upload_to_s3(local_file_path, s3_key):
    """Uploads the given file to S3 and returns the S3 URI."""
    try:
        print(f"Uploading file: {local_file_path}")
        print(f"Bucket: {BUCKET_NAME}, S3 Key: {s3_key}")
        s3.upload_file(local_file_path, BUCKET_NAME, s3_key)
        print("Upload successful!")
        return f"s3://{BUCKET_NAME}/{s3_key}"
    except Exception as e:
        print(f"❌ Error uploading file to S3: {e}")
        raise e

def start_transcription_job(job_name, media_file_uri):
    """Starts an AWS Transcribe job."""
    response = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": media_file_uri},
        MediaFormat="mp3",
        LanguageCode="en-US",
        OutputBucketName=BUCKET_NAME
    )
    return response

def wait_for_transcription(job_name, initial_wait=15, max_wait=300):
    """Polls until the transcription job is completed or fails, with an initial delay and maximum wait time."""
    print(f"Waiting {initial_wait} seconds before checking transcription job status...")
    time.sleep(initial_wait)
    
    total_wait = initial_wait
    while total_wait < max_wait:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = result["TranscriptionJob"]["TranscriptionJobStatus"]
        if status in ["COMPLETED", "FAILED"]:
            break
        print("🕒 Transcription in progress... Waiting 5 seconds...")
        time.sleep(5)
        total_wait += 5

    if status == "COMPLETED":
        transcript_url = result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        print("✅ Transcription completed!")
        print("Transcript URL from Transcribe:", transcript_url)
        return transcript_url
    else:
        print("❌ Transcription job failed or timed out after waiting", total_wait, "seconds.")
        return None

def download_transcript(transcript_url):
    """Downloads the transcript using a pre-signed URL and extracts the transcript text without printing the full text."""
    try:
        print("Attempting to download transcript from URL:", transcript_url)
        # Extract object key robustly
        split_marker = f"{BUCKET_NAME}/"
        if split_marker in transcript_url:
            object_key = transcript_url.split(split_marker)[-1]
        else:
            parsed_url = urlparse(transcript_url)
            object_key = parsed_url.path.lstrip('/')
        print("Extracted object key:", object_key)
        
        # Wait a bit to ensure the file is available in S3
        print("Waiting 10 seconds before generating pre-signed URL...")
        time.sleep(10)

        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': object_key},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        print("Generated presigned URL:", presigned_url)
        
        response = requests.get(presigned_url)
        print("GET response status code:", response.status_code)
        if response.status_code == 200:
            transcript_data = response.json()
            transcript_text = transcript_data["results"]["transcripts"][0]["transcript"]
            print("Downloaded transcript successfully. Transcript length:", len(transcript_text))
            return transcript_text
        else:
            print(f"❌ Failed to download transcript. HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return None

def transcribe_audio(local_audio_path):
    """
    Handles the full transcription process.
    If a transcript already exists for this file, load and return it.
    Otherwise, call AWS Transcribe, then save the transcript to a file.
    """
    transcript_file = os.path.splitext(local_audio_path)[0] + ".txt"
    if os.path.exists(transcript_file):
        print("Transcript file already exists. Using saved transcript.")
        with open(transcript_file, "r", encoding="utf-8") as f:
            return f.read()

    file_name = os.path.basename(local_audio_path)
    s3_uri = upload_to_s3(local_audio_path, file_name)
    if not s3_uri:
        print("❌ Upload to S3 failed.")
        return None

    job_name = f"QuickMeetTranscription_{int(time.time())}"
    print(f"🚀 Starting transcription job: {job_name}")
    start_transcription_job(job_name, s3_uri)

    print("⏳ Waiting for transcription to complete...")
    transcript_url = wait_for_transcription(job_name)
    if transcript_url:
        transcript_text = download_transcript(transcript_url)
        if transcript_text:
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            return transcript_text
        else:
            print("❌ Error fetching transcript.")
            return None
    else:
        print("❌ Error processing transcription.")
        return None