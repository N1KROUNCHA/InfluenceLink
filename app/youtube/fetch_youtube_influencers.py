import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_channels(query, max_results=50):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json().get("items", [])


def get_channel_details(channel_ids):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(channel_ids),
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json().get("items", [])
