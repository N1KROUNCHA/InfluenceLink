from app.ingestion.channel_discovery import discover_channels
from app.ingestion.youtube_ingest import fetch_channel_by_id

def batch_ingest(keyword):
    channel_ids = discover_channels(keyword)

    for cid in channel_ids:
        fetch_channel_by_id(cid)

    print("Batch ingestion completed")

if __name__ == "__main__":
    batch_ingest("technology")
