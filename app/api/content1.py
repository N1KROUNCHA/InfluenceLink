from fastapi import APIRouter, HTTPException
from app.content_ai.content_generator1 import generate_content
from app.db.mysql import cursor, conn
from app.db.mongo import db
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/content", tags=["Content"])

class SaveContentRequest(BaseModel):
    influencer_id: int
    campaign_id: Optional[int] = None
    prompt: Optional[str] = None
    content: str 
    trends: Optional[list] = None

@router.post("/creator-studio/save")
def save_creator_studio_content(data: SaveContentRequest):
    try:
        doc = data.dict()
        doc["generated_at"] = datetime.utcnow()
        db.influencer_content.insert_one(doc)
        return {"message": "Content saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/creator-studio/history/{influencer_id}")
def get_creator_studio_history(influencer_id: int, campaign_id: Optional[int] = None):
    try:
        query = {"influencer_id": influencer_id}
        if campaign_id:
            query["campaign_id"] = campaign_id
            
        items = list(db.influencer_content.find(query).sort("generated_at", -1))
        for item in items:
            item["_id"] = str(item["_id"])
            item["generated_at"] = item["generated_at"].isoformat()
        return items
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/{campaign_id}")
def generate_content_api(campaign_id: int):
    print(f"🎬 [Content] Starting generation for Campaign {campaign_id}")
    try:
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

        print(f"🧠 [Content] Calling AI generator with {len(influencers)} influencers and {len(trends)} trends")
        content = generate_content(brand, influencers, trends)
        print(f"✅ [Content] AI Generation complete. Length: {len(content)}")

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
    except Exception as e:
        print(f"❌ [Content Error] {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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

@router.get("/creator-studio/{influencer_id}")
def generate_creator_studio_content(influencer_id: int, prompt: str = None):
    """Generate viral content ideas for an influencer based on their DNA and optional custom prompt"""
    try:
        from app.content_ai.content_generator1 import generate_influencer_ideas
        
        cursor.execute("SELECT channel_name, category, description FROM influencers WHERE influencer_id = %s", (influencer_id,))
        influencer = cursor.fetchone()
        if not influencer:
            raise HTTPException(status_code=404, detail="Influencer not found")
        
        # Fetch category trends
        cursor.execute("SELECT trend FROM category_trends WHERE category = %s ORDER BY RAND() LIMIT 5", (influencer["category"],))
        trends = [row["trend"] for row in cursor.fetchall()]
        if not trends:
            trends = ["Viral YouTube Challenges", "Short-form Storytelling", "Niche Deep-dives"]

        ideas = generate_influencer_ideas(influencer, trends, user_prompt=prompt)

        return {
            "influencer_id": influencer_id,
            "ideas": ideas,
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
