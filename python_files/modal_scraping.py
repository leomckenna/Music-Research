import os
import json
import logging
import time
from googleapiclient.discovery import build
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(filename="youtube_scraper.log", level=logging.ERROR)

# YouTube API setup
API_KEY = "AIzaSyD1UHGH2KyewEINzDdJCGoveW8nhLFIiKc"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Load session data
session_data = pd.read_csv("davis_allsessions.csv")

# Extract unique session-specific terms
session_queries = []
for _, row in session_data.iterrows():
    datelocation = row['datelocation']
    group_name = row['group_name']
    if pd.notnull(group_name) and pd.notnull(datelocation):
        combined_entry = f"{group_name}, {datelocation}"
    elif pd.notnull(group_name):
        combined_entry = group_name
    elif pd.notnull(datelocation):
        combined_entry = datelocation
    if combined_entry and combined_entry not in session_queries:
        session_queries.append(combined_entry)

SEARCH_QUERIES = session_queries

MAX_RESULTS = 10
OUTPUT_CSV = "modal_videos_new.csv"
CACHE_FILE = "youtube_cache.json"

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
else:
    cache = {}

# Function to search YouTube
def search_youtube(query, max_results):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    ).execute()
    return response.get("items", [])

# Function to retry API requests
def search_youtube_with_retry(query, max_results, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return search_youtube(query, max_results)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                raise e

# Function to filter and extract video metadata
def extract_video_data(video_items, keywords, session_terms, max_year=1955):
    video_data = []
    for item in video_items:
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        video_id = item["id"]["videoId"]
        published_date = item["snippet"]["publishedAt"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Check if title or description contains session terms
        if any(term.lower() in (title + description).lower() for term in session_terms):
            # Exclude videos with years later than the max_year
            years_in_text = re.findall(r"\b(?:19[0-5][0-9]|1955)\b", title + description)
            if not any(int(year) > max_year for year in map(int, years_in_text)):
                video_data.append({
                    "Title": title,
                    "Description": description,
                    "Published Date": published_date,
                    "Video URL": video_url
                })
    return video_data

# Function to process a single query
def process_query(query):
    # Create a local copy of cache to avoid modifying it during iteration
    local_cache = dict(cache)
    
    if query in local_cache:
        video_items = local_cache[query]
    else:
        try:
            video_items = search_youtube_with_retry(query, max_results=MAX_RESULTS)
            # Update the global cache after fetching the data
            cache[query] = video_items
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            if "quotaExceeded" in str(e):
                print("Quota exceeded. Stopping the script.")
                raise e
            else:
                logging.error(f"Error processing query '{query}': {e}")
                return []
    return extract_video_data(video_items, keywords=["live", "modal jazz", "performance", "concert", "recording", "session"], 
                              session_terms=session_data['datelocation'].dropna().tolist() + session_data['group_name'].dropna().tolist())


# Main function to collect data
def collect_modal_videos():
    all_video_data = []
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(process_query, SEARCH_QUERIES)
            for result in results:
                all_video_data.extend(result)
    except Exception as e:
        logging.error(f"Unexpected error during processing: {e}")

    if all_video_data:
        df = pd.DataFrame(all_video_data)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Data saved to {OUTPUT_CSV}")
    else:
        print("No video data collected.")

# Run the script
if __name__ == "__main__":
    collect_modal_videos()
