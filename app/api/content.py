from fastapi import APIRouter, HTTPException
from app.db.mysql import cursor
from app.db.mongo import db
from app.content_ai.content_generator import generate_content

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/generate/{campaign_id}")
def generate_campaign_content(campaign_id: int):

    # Campaign
    cursor.execute("SELECT * FROM campaigns WHERE campaign_id=%s", (campaign_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")

    columns = [c[0] for c in cursor.description]
    brand = dict(zip(columns, row))

    # Influencers from ranking table
    cursor.execute("""
        SELECT i.influencer_id, i.style
        FROM ranking_scores r
        JOIN influencers i ON i.influencer_id = r.influencer_id
        WHERE r.campaign_id = %s
        LIMIT 20
    """, (campaign_id,))
    influencer_rows = cursor.fetchall()

    influencers = []
    for r in influencer_rows:
        influencer_id, style = r
        doc = db.influencer_dna.find_one({"influencer_id": influencer_id})

        influencers.append({
            "style": style,
            "topics": doc.get("topics", []) if doc else []
        })

    # You can later plug real trends here
    trends = []

    content = generate_content(brand, influencers, trends)

    return {
        "campaign_id": campaign_id,
        "content": content
    }
         
