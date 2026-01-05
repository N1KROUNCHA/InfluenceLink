from fastapi import APIRouter, HTTPException
from app.content_ai.content_generator1 import generate_content
from app.db.mysql import cursor, conn
from app.db.mongo import db
from datetime import datetime

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/generate/{campaign_id}")
def generate_content_api(campaign_id: int):

    cursor.execute("""
        SELECT title, category, target_region, required_style
        FROM campaigns
        WHERE campaign_id = %s
    """, (campaign_id,))

    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand = {
        "title": row["title"],
        "category": row["category"],
        "target_region": row["target_region"],
        "required_style": row["required_style"],
    }

    cursor.execute("""
        SELECT i.influencer_id, i.style
        FROM influencers i
        JOIN ranking_scores r ON i.influencer_id = r.influencer_id
        WHERE r.campaign_id = %s
        ORDER BY r.rank_position
        LIMIT 10
    """, (campaign_id,))

    influencers = []
    for r in cursor.fetchall():
        influencers.append({
            "influencer_id": r["influencer_id"],
            "style": r["style"]
        })

    cursor.execute("""
    SELECT trend
    FROM category_trends
    WHERE category = %s
    ORDER BY RAND()
    LIMIT 5
""", (brand["category"],))
    trends = [row["trend"] for row in cursor.fetchall()]
    if not trends:
        trends = [brand["category"]]

    content = generate_content(brand, influencers, trends)

    # Save generated content to MongoDB
    content_doc = {
        "campaign_id": campaign_id,
        "content": content,
        "generated_at": datetime.utcnow(),
        "influencer_count": len(influencers),
        "trends_used": trends
    }
    db.generated_content.insert_one(content_doc)

    return {
        "campaign_id": campaign_id,
        "content": content,
        "saved": True
    }


@router.get("/history/{campaign_id}")
def get_content_history(campaign_id: int, limit: int = 10):
    """Get previously generated content for a campaign"""
    contents = list(
        db.generated_content.find(
            {"campaign_id": campaign_id}
        )
        .sort("generated_at", -1)
        .limit(limit)
    )
    
    # Convert ObjectId to string for JSON serialization
    for content in contents:
        content["_id"] = str(content["_id"])
        if "generated_at" in content:
            content["generated_at"] = content["generated_at"].isoformat()
    
    return {
        "campaign_id": campaign_id,
        "count": len(contents),
        "history": contents
    }


@router.get("/latest/{campaign_id}")
def get_latest_content(campaign_id: int):
    """Get the most recently generated content for a campaign"""
    latest = db.generated_content.find_one(
        {"campaign_id": campaign_id},
        sort=[("generated_at", -1)]
    )
    
    if not latest:
        raise HTTPException(
            status_code=404, 
            detail="No content generated for this campaign yet"
        )
    
    latest["_id"] = str(latest["_id"])
    if "generated_at" in latest:
        latest["generated_at"] = latest["generated_at"].isoformat()
    
    return latest
