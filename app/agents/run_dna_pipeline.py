from app.db.mysql import cursor
from app.agents.influencer_dna.dna_builder import build_influencer_dna


def run_dna_pipeline():
    cursor.execute("""
        SELECT influencer_id, channel_id, channel_name
        FROM influencers
    """)

    influencers = cursor.fetchall()
    print(f"🔍 Found {len(influencers)} influencers")

    success = 0

    for influencer_id, channel_id, channel_name in influencers:
        try:
            channel_doc = {
                "id": channel_id,
                "snippet": {
                    "title": channel_name or "",
                    "description": channel_name or "",
                    "thumbnails": {
                        "high": {"url": ""}
                    }
                }
            }

            build_influencer_dna(channel_doc, influencer_id)
            success += 1

        except Exception as e:
            print(f"⚠️ Failed for influencer {influencer_id}: {e}")

    print(f"✅ Influencer DNA pipeline completed ({success}/{len(influencers)})")


if __name__ == "__main__":
    run_dna_pipeline()
