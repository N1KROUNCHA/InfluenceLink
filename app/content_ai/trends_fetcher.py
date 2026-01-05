import requests
import os

SERP_API_KEY = os.getenv("SERPAPI_KEY")

def get_trending_topics(category: str):
    if not SERP_API_KEY:
        return []

    params = {
        "engine": "google_trends",
        "q": category,
        "geo": "IN",
        "api_key": SERP_API_KEY
    }

    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = r.json()

        trends = []
        for item in data.get("interest_over_time", {}).get("timeline_data", [])[:5]:
            trends.append(item.get("formattedValue"))

        return list(set(trends))
    except:
        return []
