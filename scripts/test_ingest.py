from app.ingestion.youtube_ingest import get_channel_id, fetch_channel_by_id

cid = get_channel_id("Veritasium")
fetch_channel_by_id(cid)
