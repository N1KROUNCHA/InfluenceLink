from app.ingestion.youtube_ingest import fetch_channel
from app.db.mysql import cursor

def ingest_for_campaign(campaign):
    query = """
    SELECT channel_id FROM influencers
    WHERE subscriber_count BETWEEN %s AND %s
    """
    cursor.execute(query, (
        campaign["min_subscribers"],
        campaign["max_subscribers"]
    ))
    channels = cursor.fetchall()

    if not channels:
        # fallback → discover new channels
        from app.ingestion.discover_channels import discover_channels
        channels = discover_channels(campaign["category"])

    for ch in channels:
        fetch_channel(ch[0])
