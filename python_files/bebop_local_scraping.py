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
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define local path for saving files
LOCAL_PATH = "/Users/leomckenna/Desktop/Music Research/"

# Setup logging
LOG_FILE = os.path.join(LOCAL_PATH, "youtube_scraper.log")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# YouTube API setup with multiple API keys for rotation
API_KEYS = [
    "AIzaSyD1UHGH2KyewEINzDdJCGoveW8nhLFIiKc",
    "AIzaSyCkzJl0Rxm2eEOj_urGDyp3DEPDDtDeCIQ",
    "AIzaSyB19jMObUcK5UpM9ZDt9HO7TOV8DX-KlBE",
    "AIzaSyBFa02uluT2ZPTD8By8KxJi3QCkq-5jdCI",
    "AIzaSyAFTpKwgJOWVUJweW_ajbvMI1d8YjsRVHU",
    "AIzaSyBzMuNSl2JpCo4mf_3QfArCMMKlPBksrTs",
    "AIzaSyB0jTpl2tvaiA_hVL6vyE98YSG_IKaJhfA",
    "AIzaSyAr-INrfcxR9_6ahsB2Fb4vZSknNoHsJAY",
    "AIzaSyBD7N7HPKBI8cKLvlNkNHvJn3t4WV2WW5I",
    "AIzaSyC1uNVX2Pf3vRekAFujmTVTa82kqJEBvO0",
    "AIzaSyDTuyaUwYsWtsoPTEv2wgMAJHgzF1IBy4g",
    "AIzaSyBMUpB9iTKixV94z9-ZUmcyDfT6tJ5QFVY",
    "AIzaSyCPxHCGty4zadYFBt_9f031sIbL1Dd2zVA",
    "AIzaSyC77YNfgnaZBqBwzGZ_ZI7z4XP6Ah8rCmc",
    "AIzaSyBgNgfZfffPeuD1pcN92y-U-I7LJT3-Q-I",
    "AIzaSyDYMROM-dn2Tg5Zh0NfiUq9VwmOVEPUSBI",
    "AIzaSyDs4FuliVn3TE8rg0TPQE_zbYYQNDMYMHk",
    "AIzaSyC7nbL3zSzowGaH0PrzqIPvTi-SYDvFioE",
    "AIzaSyA9suEKIlq2qm6MEjhWnsmxCkKWhsJgBLc",
    "AIzaSyCqNDwZ8A6r6B91TdsxUC80n4haVVWAOxY",
    "AIzaSyC5W-VmRvpXCV1tbIB7JTedHf0cVmTM-FA",
    "AIzaSyAzXQ4jENbZWRdjSul_xFBnLhhyW04RBxU",
    "AIzaSyCCRvAA13zRUbXqH3RnY3ejZSuwfVb2g8A",
    "AIzaSyD2mi7rilV-lfIMMGtsetkOeDiJivgE7Kk",
    "AIzaSyBgk_IC0ZRaIqecQO2UpGlKOyl51AmMoO4",
    "AIzaSyDd_61vqCZuxJOb5m8Bp9wnXSBi8lMnfLQ",
    "AIzaSyBgMKdx5PDLkplaKh89VvuqsAWr29adDJE",
    "AIzaSyDVoQv3uMKSJlGCFooA41vAeT6sU2hbWOM",
    "AIzaSyAc_vUl_F22-VJnPisj_-aP7khzUqvDJ5o",
    "AIzaSyAi5hdFBMAGEfGiYYUXWUsn5PsE0yDqzD8",
    "AIzaSyAfhsvdr1em_iYqd5nkj2B_NmWvQqBXnU0",
    "AIzaSyDUYAUBZggphwZTwwMbZY7ni_B810hLBMU",
    "AIzaSyAMpO2h_g2pb1BzmhN7mdT_VDjtF9UI0sA",
    "AIzaSyC3dRO2aRTGVIR7fERE3CUlH-j1Q5hXrac"
]  
current_api_key_index = 0
QUERY_COUNT = 0  # Track number of queries per key

# YouTube API setup
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Paths to input/output files
SESSION_CSV = os.path.join(LOCAL_PATH, "control_forleo.csv")
OUTPUT_CSV = os.path.join(LOCAL_PATH, "control_files.csv")
CACHE_FILE = os.path.join(LOCAL_PATH, "youtube_cache.json")

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
DELAY = 2  # Reduce initial delay for faster retries
MAX_RETRIES = 3  # Limit retries to avoid long hangs
CACHE_EXPIRY_DAYS = 7
MAX_WORKERS = min(20, multiprocessing.cpu_count() * 2)  # Increased workers

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                cache_data = json.load(f)
                if isinstance(cache_data, dict):
                    # Ensure each entry has a 'timestamp'
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
        cache_copy = cache.copy()  # Snapshot to prevent 'changed size' error
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
        logging.error("⚠️ All API keys exhausted. Exiting script early.")
        print("⚠️ All API keys exhausted. Exiting script early.")
        save_cache()  # Ensure progress is saved before exiting
        sys.exit("🚨 Exiting script: All API keys exhausted.")

    print(f"🔄 Switching API key to: {API_KEYS[current_api_key_index]}")
    return API_KEYS[current_api_key_index]


# Get YouTube API client
def get_youtube_client():
    global QUERY_COUNT, current_api_key_index

    QUERY_COUNT += 1
    if QUERY_COUNT >= 5:  # Rotate API key every 5 queries
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

    print(f"🔍 Query: '{query}' → {len(video_items)} videos found")
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

def extract_video_data(video_items, processed_video_ids, session_terms):
    video_data = []
    for item in video_items:
        video_id = item["id"]["videoId"]

        if video_id in processed_video_ids:
            continue

        title = item["snippet"]["title"]
        description = item["snippet"]["description"]

        if "charlie parker" in title.lower() or "charlie parker" in description.lower() \
                or "bird" in title.lower() or "bird" in description.lower():
            continue

        published_date = item["snippet"]["publishedAt"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        if any(term.lower() in (title + description).lower() for term in session_terms):
            video_data.append({
                "Title": title,
                "Description": description,
                "Published Date": published_date,
                "Video URL": video_url
            })
            processed_video_ids.add(video_id)

    return video_data

# Process a single query
def process_query(query, processed_video_ids):
    if query in cache:
        video_items = cache[query]["videos"]
    else:
        video_items = search_youtube_with_retry(query)
        cache[query] = {"videos": video_items, "timestamp": time.time()}

        # Efficient cache saving — save every 20 queries
        if len(cache) % 20 == 0:
            save_cache()

    extracted_data = extract_video_data(
        video_items, 
        processed_video_ids,
        session_terms=session_data['datelocation'].tolist() + session_data['group_name'].tolist()
    )

    print(f"📊 Extracted {len(extracted_data)} items from query: {query}")
    
    # ✅ Immediate CSV Save for Each Successful Query
    if extracted_data:
        pd.DataFrame(extracted_data).to_csv(
            OUTPUT_CSV,
            mode="a", 
            header=not os.path.exists(OUTPUT_CSV), 
            index=False
        )
        print(f"✅ {len(extracted_data)} new records saved to {OUTPUT_CSV}")
    
    return extracted_data if extracted_data else []  # Ensure empty results don't block data flow

# Collect and save video data
def collect_control_videos():
    all_video_data = []
    processed_video_ids = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(lambda q: process_query(q, processed_video_ids), SEARCH_QUERIES)
        for result in results:
            all_video_data.extend(result)

    print(f"📋 Total collected data entries: {len(all_video_data)}")

    if all_video_data:  # ✅ Only save if data exists
        pd.DataFrame(all_video_data).to_csv(
            OUTPUT_CSV, 
            mode="a", 
            header=not os.path.exists(OUTPUT_CSV), 
            index=False
        )
        print(f"✅ Data saved to {OUTPUT_CSV} ({len(all_video_data)} new videos)")
    else:
        print("⚠️ No data found. CSV not created.")


# Run script
if __name__ == "__main__":
    collect_control_videos()
