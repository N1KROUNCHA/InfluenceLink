from fastapi import APIRouter, HTTPException
from app.db.mysql import cursor, conn
from app.agents.brand_dna.brand_dna_builder import build_brand_dna
from app.aiml.build_campaign_training_data import build_campaign_training_data
from app.aiml.train_campaign_match_model import train_campaign_model
from app.aiml.predict_campaign_ranking import predict_campaign_ranking

router = APIRouter(prefix="/campaigns")


@router.post("/create")
def create_campaign(data: dict):
    cursor.execute("""
        INSERT INTO campaigns (
            brand_id, title, category, budget,
            min_subscribers, max_subscribers,
            target_region, target_language,
            required_style, authenticity_threshold,
            dna_similarity_threshold, status
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'active')
    """, (
        data["brand_id"],
        data["campaign_name"],
        data["category"],
        data["budget"],
        data["min_subscribers"],
        data["max_subscribers"],
        data["target_region"],
        data["target_language"],
        data["required_style"],
        data["authenticity_threshold"],
        data["dna_similarity_threshold"]
    ))

    campaign_id = cursor.lastrowid
    conn.commit()

    # PIPELINE
    build_brand_dna({
        "campaign_id": campaign_id,
        "title": data["campaign_name"],
        "category": data["category"],
        "target_region": data["target_region"],
        "required_style": data["required_style"]
    })

    build_campaign_training_data(campaign_id)
    train_campaign_model()
    predict_campaign_ranking(campaign_id)

    return {
        "message": "Campaign created and ranked successfully",
        "campaign_id": campaign_id
    }


@router.get("/recommend/{campaign_id}")
def recommend(campaign_id: int):
    cursor.execute("""
        SELECT r.rank_position, r.normalized_score, r.confidence_level,
               i.channel_id, i.channel_name, c.title
        FROM ranking_scores r
        JOIN influencers i ON i.influencer_id = r.influencer_id
        JOIN campaigns c ON c.campaign_id = r.campaign_id
        WHERE r.campaign_id = %s
        ORDER BY r.rank_position
        LIMIT 10
    """, (campaign_id,))

    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(404, "No recommendations")

    return {
        "campaign_id": campaign_id,
        "recommendations": [
            {
                "rank": r[0],
                "score": float(r[1]),
                "confidence": float(r[2]),
                "channel_id": r[3],
                "channel_name": r[4],
                "campaign": r[5]
            }
            for r in rows
        ]
    }
