def normalize_channel(channel):
    stats = channel["statistics"]
    snippet = channel["snippet"]

    subs = int(stats.get("subscriberCount", 0))
    views = int(stats.get("viewCount", 0))
    videos = int(stats.get("videoCount", 0))

    avg_views = views / max(videos, 1)

    engagement_score = min(1.0, (avg_views / max(subs, 1)))

    return {
        "channel_id": channel["id"],
        "channel_name": snippet["title"],
        "category": "fitness",  # inferred later via NLP
        "primary_language": snippet.get("defaultLanguage", "en"),
        "region": snippet.get("country", "India"),
        "subscriber_count": subs,
        "avg_views": avg_views,
        "like_ratio": 0.05,
        "comment_ratio": 0.01,
        "engagement_score": engagement_score,
        "authenticity_score": round(min(1.0, engagement_score + 0.2), 2),
        "style": "motivational",
        "video_count": videos
    }
