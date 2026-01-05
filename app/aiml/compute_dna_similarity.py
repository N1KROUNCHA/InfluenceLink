import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.db.mysql import cursor, conn
from app.db.mongo import db

def compute_dna_similarity():
    campaigns = list(db.campaign_dna.find({}))
    influencers = list(db.influencer_dna.find({}))

    for camp in campaigns:
        camp_emb = np.array(camp["embedding"]).reshape(1, -1)

        for inf in influencers:
            inf_emb = np.array(inf["embedding"]).reshape(1, -1)

            sim = cosine_similarity(camp_emb, inf_emb)[0][0]

            cursor.execute("""
                INSERT INTO dna_similarity (campaign_id, influencer_id, similarity_score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE similarity_score = VALUES(similarity_score)
            """, (
                camp["campaign_id"],
                inf["influencer_id"],
                float(sim)
            ))

    conn.commit()
    print("✅ DNA similarity computed")

if __name__ == "__main__":
    compute_dna_similarity()
