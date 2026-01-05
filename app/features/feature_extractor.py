from datetime import datetime

def extract_raw_features(channel_doc):
    stats = channel_doc.get("statistics", {})
    snippet = channel_doc.get("snippet", {})

    return {
        "channel_id": channel_doc.get("id"),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "channel_age_years": calculate_channel_age(
            snippet.get("publishedAt")
        )
    }


def calculate_channel_age(published_at):
    if not published_at:
        return 0

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",        # without milliseconds
        "%Y-%m-%dT%H:%M:%S.%fZ"      # with milliseconds
    ]

    for fmt in formats:
        try:
            published_date = datetime.strptime(published_at, fmt)
            today = datetime.utcnow()
            return round((today - published_date).days / 365, 2)
        except ValueError:
            continue

    # If all formats fail
    return 0
