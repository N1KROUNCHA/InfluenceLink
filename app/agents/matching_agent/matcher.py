from app.db.mongo import db
from app.db.mysql import conn, cursor
from app.agents.matching_agent.embedder import embed_text
from app.agents.matching_agent.scorer import cosine_similarity, final_score

def run_matcher(campaign_id: int):
    # 1️⃣ Fetch campaign
    cursor.execute("""
        SELECT title, description
        FROM campaigns
        WHERE campaign_id = %s
    """, (campaign_id,))
    campaign = cursor.fetchone()

    if not campaign:
        raise Exception("Campaign not found")

    campaign_text = f"{campaign[0]} {campaign[1]}"
    campaign_embedding = embed_text(campaign_text)

    # 2️⃣ Fetch influencer DNA
    influencers = list(db.influencer_dna.find())

    results = []

    for inf in influencers:
        sim = cosine_similarity(
            campaign_embedding,
            inf["embedding"]
        )

        engagement = inf.get("engagement_score", 0.0)
        authenticity = inf.get("authenticity_score", 0.8)  # default

        score = final_score(sim, engagement, authenticity)

        results.append({
            "channel_id": inf["channel_id"],
            "score": score
        })

    # 3️⃣ Rank
    results.sort(key=lambda x: x["score"], reverse=True)

    return results
