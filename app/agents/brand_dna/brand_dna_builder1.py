from app.agents.influencer_dna.nlp_agent import extract_nlp_profile
from app.db.mongo import db

def build_brand_dna(campaign):
    text = " ".join([
        campaign["title"],
        campaign.get("description", ""),
        campaign.get("category", "")
    ])

    profile = extract_nlp_profile(text)

    db.brand_dna.update_one(
        {"campaign_id": campaign["campaign_id"]},
        {"$set": profile},
        upsert=True
    )
