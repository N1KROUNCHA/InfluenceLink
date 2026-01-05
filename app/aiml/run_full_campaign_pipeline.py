from app.agents.brand_dna.brand_dna_builder import build_brand_dna
from app.aiml.run_campaign_matching import run_campaign_matching
from app.aiml.build_campaign_training_data import build_campaign_training_data
from app.aiml.enrich_campaign_features import enrich_campaign_features
from app.aiml.train_campaign_match_model import train_model
from app.aiml.predict_campaign_ranking import predict_campaign_ranking


def run_full_campaign_pipeline(campaign_id: int, campaign_payload: dict):
    print(f"🚀 Running full AI pipeline for campaign {campaign_id}")

    # 1️⃣ Build brand DNA
    build_brand_dna({
        "campaign_id": campaign_id,
        "title": campaign_payload["campaign_name"],
        "description": campaign_payload.get("description", ""),
        "category": campaign_payload["category"]
    })
    print("✅ Brand DNA built")

    # 2️⃣ Match influencers using embeddings
    run_campaign_matching(campaign_id)
    print("✅ DNA similarity computed")

    # 3️⃣ Build campaign training rows
    build_campaign_training_data()
    print("✅ Campaign training data built")

    # 4️⃣ Enrich features (authenticity, style, etc.)
    enrich_campaign_features()
    print("✅ Feature enrichment completed")

    # 5️⃣ Train / update ML model
    train_model()
    print("✅ Model trained")

    # 6️⃣ Predict rankings
    predict_campaign_ranking(campaign_id)
    print("✅ Rankings generated")

    return True
