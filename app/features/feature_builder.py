from datetime import datetime

def calculate_channel_age(published_at: str) -> float:
    """
    Calculate channel age in years from ISO datetime string
    """
    try:
        published_date = datetime.strptime(
            published_at.replace("Z", ""), "%Y-%m-%dT%H:%M:%S"
        )
    except ValueError:
        # fallback for microseconds
        published_date = datetime.strptime(
            published_at.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
        )

    today = datetime.utcnow()
    age_years = (today - published_date).days / 365
    return round(age_years, 2)


def build_features(raw: dict) -> dict:
    """
    Build AIML features from raw influencer data
    """

    # --- Raw values (safe access) ---
    subs = int(raw.get("subscriber_count", 0))
    views = int(raw.get("total_views", 0))
    videos = int(raw.get("video_count", 0))
    published_at = raw.get("published_at")

    # --- Derived values ---
    channel_age_years = (
        calculate_channel_age(published_at)
        if published_at else 0
    )

    avg_views_per_video = (
        views / videos if videos > 0 else 0
    )

    # Simple engagement proxy (baseline)
    engagement_score = (
        avg_views_per_video / subs if subs > 0 else 0
    )

    # --- Final engineered feature set ---
    features = {
        "subscriber_count": subs,
        "video_count": videos,
        "channel_age_years": channel_age_years,
        "avg_views": round(avg_views_per_video, 2),
        "engagement_score": round(engagement_score, 4)
    }

    return features
