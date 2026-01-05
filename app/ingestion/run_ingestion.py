from app.ingestion.discover_channels import discover_channels
from app.ingestion.ingest_channels import ingest_channel

def run_ingestion(keyword):
    channel_ids = discover_channels(keyword)

    print(f"Discovered {len(channel_ids)} channels")

    for cid in channel_ids:
        ingest_channel(cid)
        print(f"Ingested: {cid}")

if __name__ == "__main__":
    run_ingestion("technology")
