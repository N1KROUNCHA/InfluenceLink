from app.agents.video_agent.fetch_videos import fetch_recent_videos
from app.db.mongo import db

def run_video_ingestion():
    influencers = list(db.influencers_full.find({}, {"id": 1}))

    if not influencers:
        print("❌ No influencers found")
        return

    for inf in influencers:
        channel_id = inf["id"]
        videos = fetch_recent_videos(channel_id, max_results=10)

        if not videos:
            continue

        # Delete old videos of this channel
        db.videos.delete_many({"channel_id": channel_id})

        # Insert only latest videos
        db.videos.insert_many(videos)

        print(f"✅ Stored {len(videos)} videos for {channel_id}")

    print("\n🎉 Video ingestion completed")

if __name__ == "__main__":
    run_video_ingestion()
