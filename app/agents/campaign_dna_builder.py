from sentence_transformers import SentenceTransformer
from app.db.mongo import db
from app.db.mysql import cursor

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_campaign_dna():
    cursor.execute("SELECT campaign_id, title, category FROM campaigns")
    campaigns = cursor.fetchall()

    for c in campaigns:
        text = f"{c[1]} {c[2]}"
        emb = model.encode(text).tolist()

        db.campaign_dna.update_one(
            {"campaign_id": c[0]},
            {"$set": {
                "campaign_id": c[0],
                "embedding": emb,
                "category": c[2]
            }},
            upsert=True
        )

    print("✅ Campaign DNA built")

if __name__ == "__main__":
    build_campaign_dna()
