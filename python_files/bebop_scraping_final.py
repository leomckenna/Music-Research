import os
import json
import logging
import time
import random
import multiprocessing
import pandas as pd
import re
import sys
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from load_api_keys import get_api_keys


# Define path for saving files
BASE_DIR = os.path.expanduser("~/projects/youtube_scraper/")

# Setup logging
LOG_FILE = os.path.join(BASE_DIR, "youtube_scraper.log")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# YouTube API setup with multiple API keys for rotation
API_KEYS = get_api_keys()

current_api_key_index = 0
QUERY_COUNT = 0

# YouTube API setup
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Paths to input/output files
SESSION_CSV = os.path.join(BASE_DIR, "parker_allsessions_forleo.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "bebop_files.csv")
CACHE_FILE = os.path.join(BASE_DIR, "youtube_cache.json")
WAV_OUTPUT_DIR = os.path.join(BASE_DIR, "wav_files")

# Create output directory for WAV files
os.makedirs(WAV_OUTPUT_DIR, exist_ok=True)

# Load session data
if not os.path.exists(SESSION_CSV):
    raise FileNotFoundError(f"Session CSV file not found at {SESSION_CSV}")

session_data = pd.read_csv(SESSION_CSV)

# Validate required columns
if not all(col in session_data.columns for col in ['datelocation', 'group_name']):
    raise ValueError("Missing required columns in session CSV.")

session_data.dropna(subset=['datelocation', 'group_name'], inplace=True)

# Generate unique search queries with variations
ADDITIONAL_KEYWORDS = ["full set", "full concert", "rare footage", "archival", "classic", "unreleased"]

SEARCH_QUERIES = [
    f"{row['datelocation']} {row['group_name']} live OR session OR concert OR gig OR performance OR jazz OR bebop OR set OR recording"
    for _, row in session_data.iterrows()
]

EXPANDED_QUERIES = []
for query in SEARCH_QUERIES:
    EXPANDED_QUERIES.append(query)
    for keyword in ADDITIONAL_KEYWORDS:
        EXPANDED_QUERIES.append(f"{query} {keyword}")

# Remove duplicates and shuffle queries
SEARCH_QUERIES = list(set(EXPANDED_QUERIES))
random.shuffle(SEARCH_QUERIES)

# Constants
MAX_RESULTS = 50
DELAY = 10
MAX_RETRIES = 10
CACHE_EXPIRY_DAYS = 7
MAX_WORKERS = min(20, multiprocessing.cpu_count() * 2)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                cache_data = json.load(f)
                if isinstance(cache_data, dict):
                    return {
                        k: v for k, v in cache_data.items()
                        if isinstance(v, dict) and v.get("timestamp", 0) > time.time() - (CACHE_EXPIRY_DAYS * 86400)
                    }
            except json.JSONDecodeError:
                logging.error("Cache file is corrupted. Reinitializing as an empty dictionary.")
                return {}
    return {}

cache = load_cache()

# Save cache to file
def save_cache():
    try:
        cache_copy = cache.copy()
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_copy, f, indent=4)
        print("✅ Cache saved successfully.")
    except Exception as e:
        print(f"❌ Error saving cache: {e}")
        logging.error(f"Error saving cache: {e}")

# Switch API key when quota is exceeded
def switch_api_key():
    global current_api_key_index
    current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)

    if current_api_key_index == 0:
        print("⚠️ All API keys exhausted. Exiting script early.")
        sys.exit("🚨 Exiting script: All API keys exhausted.")

    print(f"🔄 Switching API key to: {API_KEYS[current_api_key_index]}")
    return API_KEYS[current_api_key_index]

# Get YouTube API client
def get_youtube_client():
    global QUERY_COUNT, current_api_key_index

    QUERY_COUNT += 1
    if QUERY_COUNT >= 50:
        QUERY_COUNT = 0
        switch_api_key()

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEYS[current_api_key_index])

# Search YouTube videos with pagination
def search_youtube(query, max_results=MAX_RESULTS):
    youtube = get_youtube_client()
    video_items = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            pageToken=next_page_token
        )

        response = request.execute()
        video_items.extend(response.get("items", []))
        next_page_token = response.get("nextPageToken")

        if not next_page_token or len(video_items) >= 500:
            break

    return video_items

# Retry YouTube search with exponential backoff
def search_youtube_with_retry(query):
    delay = DELAY

    for attempt in range(MAX_RETRIES):
        try:
            return search_youtube(query)
        except HttpError as e:
            error_message = str(e).lower()

            if "quotaexceeded" in error_message:
                logging.error(f"Quota exceeded with API key {API_KEYS[current_api_key_index]}. Switching keys.")
                switch_api_key()
            elif "403" in error_message:
                logging.error(f"403 Forbidden error — possible API key ban: {e}")
                switch_api_key()
            elif "500" in error_message or "503" in error_message:
                logging.error(f"Server error encountered, retrying: {e}")
                time.sleep(delay * (2 ** attempt))
            else:
                logging.error(f"Unhandled API error: {e}")
                return []
        except Exception as e:
            logging.error(f"General error in API request: {e}")
            time.sleep(delay * (2 ** attempt))
    return []

# Extract video data
def extract_video_data(video_items, processed_video_ids):
    video_data = []
    for item in video_items:
        video_id = item["id"]["videoId"]

        if video_id in processed_video_ids:
            continue

        title = item["snippet"]["title"]
        description = item["snippet"]["description"]

        published_date = item["snippet"]["publishedAt"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        video_data.append({
            "Title": title,
            "Description": description,
            "Published Date": published_date,
            "Video URL": video_url
        })
        processed_video_ids.add(video_id)

    return video_data

# Process query
def process_query(query, processed_video_ids):
    video_items = search_youtube(query)
    extracted_data = extract_video_data(video_items, processed_video_ids)

    if extracted_data:
        pd.DataFrame(extracted_data).to_csv(
            OUTPUT_CSV,
            mode="a",
            header=not os.path.exists(OUTPUT_CSV),
            index=False
        )
        print(f"✅ {len(extracted_data)} new records saved to {OUTPUT_CSV}")
    
    return extracted_data

# WAV Output Directory
WAV_OUTPUT_DIR = os.path.join(LOCAL_PATH, "wav_files")
os.makedirs(WAV_OUTPUT_DIR, exist_ok=True)

# Collect video data
def collect_control_videos():
    processed_video_ids = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(lambda q: process_query(q, processed_video_ids), SEARCH_QUERIES)

    print(f"✅ Data saved to {OUTPUT_CSV}")

# Download and convert videos to WAV
def download_and_convert_to_wav(video_url, output_dir):
    try:
        # Create temp directory for downloads
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        # yt-dlp options to download best audio format
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            }


        print(f"🎧 Downloading: {video_url}")

        # Download audio
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_file = ydl.prepare_filename(info)

        # Ensure the downloaded file exists before attempting conversion
        if not os.path.exists(downloaded_file):
            raise FileNotFoundError(f"Downloaded file not found: {downloaded_file}")

        # Convert downloaded audio to WAV using pydub
        print(f"🔄 Converting: {downloaded_file}")
        audio = AudioSegment.from_file(downloaded_file)
        wav_file = os.path.join(output_dir, os.path.splitext(os.path.basename(downloaded_file))[0] + ".wav")
        audio.export(wav_file, format="wav")

        print(f"✅ Converted and saved: {wav_file}")

        # Clean up temporary files
        os.remove(downloaded_file)
        os.rmdir(temp_dir)

    except Exception as e:
        print(f"❌ Error processing {video_url}: {e}")
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"{video_url}: {e}\n")

# Process CSV file and download WAV files
def download_wav_files():
    try:
        df = pd.read_csv(OUTPUT_CSV)

        if "Video URL" not in df.columns:
            print("❗ Error: 'Video URL' column not found in CSV.")
            return

        for _, row in df.iterrows():
            video_url = row.get("Video URL")
            if pd.notna(video_url) and "youtube.com" in video_url:
                download_and_convert_to_wav(video_url, WAV_OUTPUT_DIR)

        print(f"✅ WAV files saved to {WAV_OUTPUT_DIR}")

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

# Run script
if __name__ == "__main__":
    collect_control_videos()
    download_wav_files()
