from app.db.mongo import db
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_brand_dna(data: dict):
    text = f"""
    {data.get("title","")}
    {data.get("category","")}
    {data.get("target_region","")}
    {data.get("required_style","")}
    """

    embedding = model.encode(text).tolist()

    doc = {
        "campaign_id": data["campaign_id"],
        "topics": [data.get("category")],
        "embedding": embedding,
        "style": data.get("required_style"),
        "region": data.get("target_region")
    }

    db.campaign_dna.update_one(
        {"campaign_id": data["campaign_id"]},
        {"$set": doc},
        upsert=True
    )
