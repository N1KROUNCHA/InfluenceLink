from app.agents.youtube.fetch_channels import search_channels
from app.agents.youtube.channel_stats import fetch_channel_stats
from app.agents.youtube.save_to_db import save_influencers


CATEGORIES = [
    "technology",
    "fitness",
    "beauty",
    "education",
    "finance",
    "gaming",
    "travel",
    "food",
    "fashion",
    "science"
]


def run_all():
    TOTAL_IMPORTED = 0

    for category in CATEGORIES:
        print("\n" + "=" * 60)
        print(f"🔍 Fetching influencers for category: {category.upper()}")
        print("=" * 60)

        try:
            # Step 1: Search YouTube
            channels = search_channels(
                query=category,
                max_results=200
            )

            if not channels:
                print(f"⚠️ No channels found for {category}")
                continue

            channel_ids = [c["channel_id"] for c in channels]

            # Step 2: Fetch channel stats
            stats = fetch_channel_stats(channel_ids)

            if not stats:
                print(f"⚠️ No stats fetched for {category}")
                continue

            # Step 3: Save to DB
            inserted = save_influencers(stats)
            TOTAL_IMPORTED += inserted

            print(f"✅ {inserted} influencers saved for '{category}'")

        except Exception as e:
            print(f"❌ Error processing category {category}: {e}")

    print("\n🎯 DONE")
    print(f"✅ Total influencers inserted/updated: {TOTAL_IMPORTED}")


if __name__ == "__main__":
    run_all()
