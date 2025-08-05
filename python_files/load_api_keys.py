from dotenv import load_dotenv
import os

def get_api_keys():
    load_dotenv()
    keys = []
    i = 1
    while True:
        key = os.getenv(f"API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    return keys
