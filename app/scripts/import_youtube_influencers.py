from app.youtube.fetch_youtube_influencers import search_channels, get_channel_details
from app.youtube.normalize_channel import normalize_channel
from app.youtube.save_influencers import save_influencer

QUERIES = [
    "fitness motivation",
    "home workout",
    "gym transformation",
    "weight loss tips",
    "health coach"
]

def import_influencers():
    channel_ids = []

    for q in QUERIES:
        results = search_channels(q, max_results=50)
        for item in results:
            channel_ids.append(item["snippet"]["channelId"])

    channel_ids = list(set(channel_ids))

    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        details = get_channel_details(batch)

        for ch in details:
            influencer = normalize_channel(ch)
            save_influencer(influencer)

    print("✅ YouTube influencers imported")


if __name__ == "__main__":
    import_influencers()
