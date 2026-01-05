from fastapi import APIRouter
from app.db.mysql import cursor

router = APIRouter()

@router.get("/recommend/{campaign_id}")
def recommend_influencers(campaign_id: int):
    cursor.execute("""
        SELECT
            r.normalized_score,
            r.confidence_level,
            i.channel_id,
            i.channel_name
            c.title,
            e.explanation
        FROM ranking_scores r
        JOIN influencers i ON r.influencer_id = i.influencer_id
        JOIN campaigns c ON r.campaign_id = c.campaign_id
        LEFT JOIN ranking_explanations e
        ON e.campaign_id = r.campaign_id
        AND e.influencer_id = r.influencer_id
        WHERE r.campaign_id = %s
        ORDER BY r.normalized_score DESC
    """, (campaign_id,))

    rows = cursor.fetchall()

    recommendations = []
    for idx, row in enumerate(rows, start=1):
        recommendations.append({
            "rank": idx,
            "channel_id": row[3],
            "channel_name": row[4],
            "score": round(float(row[1]), 4),
            "confidence": round(float(row[2]), 2)
        })

    return {
        "campaign_id": campaign_id,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }
