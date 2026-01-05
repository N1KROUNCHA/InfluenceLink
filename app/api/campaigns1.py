from fastapi import APIRouter, HTTPException
from app.db.mysql import cursor, conn, lock
from app.agents.brand_dna.brand_dna_builder import build_brand_dna
from app.aiml.build_campaign_training_data1 import build_campaign_training_data
from app.aiml.train_campaign_match_model1 import train_campaign_model
from app.aiml.predict_campaign_ranking1 import predict_campaign_ranking


router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.post("/campaigns/create")
def create_campaign(data: dict):

    cursor.execute("""
        INSERT INTO campaigns
        (brand_id, title, category, target_region, required_style)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data["brand_id"],
        data["title"],
        data["category"],
        data["target_region"],
        data["required_style"]
    ))

    campaign_id = cursor.lastrowid

    return {
        "message": "Campaign created successfully",
        "campaign_id": campaign_id
    }


from fastapi import BackgroundTasks

def run_campaign_ai(campaign_id: int, data: dict):
    """Background task to run AI pipeline"""
    try:
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
        print(f"✅ AI Ranking completed for Campaign {campaign_id}")
    except Exception as e:
        print(f"❌ AI Pipeline Failed: {str(e)}")

@router.post("/create")
def create_campaign(data: dict, background_tasks: BackgroundTasks):
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
    
    # Run AI in background
    background_tasks.add_task(run_campaign_ai, campaign_id, data)

    return {
        "message": "Campaign created. AI ranking started in background.",
        "campaign_id": campaign_id
    }

@router.post("/{campaign_id}/rerank")
def trigger_ranking(campaign_id: int, background_tasks: BackgroundTasks):
    """Manually trigger AI ranking"""
    # Fetch campaign data first to pass to DNA builder if needed
    cursor.execute("SELECT * FROM campaigns WHERE campaign_id=%s", (campaign_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    data = {
        "campaign_name": row["title"],
        "category": row["category"],
        "target_region": row["target_region"],
        "required_style": row["required_style"]
    }
    
    background_tasks.add_task(run_campaign_ai, campaign_id, data)
    return {"message": "AI Ranking started in background"}


@router.get("/list")
def list_campaigns(status: str = None, limit: int = 50):
    """List all campaigns with optional status filter"""
    with lock:
        if status:
            cursor.execute("""
                SELECT campaign_id, title, category, status, budget, created_at
                FROM campaigns
                WHERE status = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT campaign_id, title, category, status, budget, created_at
                FROM campaigns
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        
        campaigns = cursor.fetchall()
    return {
        "count": len(campaigns),
        "campaigns": campaigns
    }


@router.get("/{campaign_id}")
def get_campaign(campaign_id: int):
    """Get campaign details by ID"""
    with lock:
        cursor.execute("""
            SELECT *
            FROM campaigns
            WHERE campaign_id = %s
        """, (campaign_id,))
        
        campaign = cursor.fetchone()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get recommendation count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ranking_scores
            WHERE campaign_id = %s
        """, (campaign_id,))
        rec_count = cursor.fetchone()["count"]
    
    return {
        "campaign": campaign,
        "recommendation_count": rec_count
    }


@router.patch("/{campaign_id}/status")
def update_campaign_status(campaign_id: int, status: str):
    """Update campaign status (draft, active, completed)"""
    valid_statuses = ["draft", "active", "completed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    cursor.execute("""
        UPDATE campaigns
        SET status = %s
        WHERE campaign_id = %s
    """, (status, campaign_id))
    conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "message": f"Campaign {campaign_id} status updated to {status}",
        "campaign_id": campaign_id,
        "status": status
    }


@router.get("/{campaign_id}/stats")
def get_campaign_stats(campaign_id: int):
    """Get campaign statistics"""
    with lock:
        # Check if campaign exists
        cursor.execute("SELECT campaign_id FROM campaigns WHERE campaign_id = %s", (campaign_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get recommendation stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_recommendations,
                AVG(normalized_score) as avg_score,
                MAX(normalized_score) as max_score,
                MIN(normalized_score) as min_score,
                AVG(confidence_level) as avg_confidence
            FROM ranking_scores
            WHERE campaign_id = %s
        """, (campaign_id,))
        stats = cursor.fetchone()
        
        # Get top 3 influencers
        cursor.execute("""
            SELECT i.channel_name, r.normalized_score
            FROM ranking_scores r
            JOIN influencers i ON r.influencer_id = i.influencer_id
            WHERE r.campaign_id = %s
            ORDER BY r.normalized_score DESC
            LIMIT 3
        """, (campaign_id,))
        top_influencers = cursor.fetchall()
    
    return {
        "campaign_id": campaign_id,
        "statistics": {
            "total_recommendations": stats["total_recommendations"] or 0,
            "average_score": float(stats["avg_score"]) if stats["avg_score"] else 0.0,
            "max_score": float(stats["max_score"]) if stats["max_score"] else 0.0,
            "min_score": float(stats["min_score"]) if stats["min_score"] else 0.0,
            "average_confidence": float(stats["avg_confidence"]) if stats["avg_confidence"] else 0.0
        },
        "top_influencers": [
            {
                "channel_name": inf["channel_name"],
                "score": float(inf["normalized_score"])
            }
            for inf in top_influencers
        ]
    }


@router.get("/recommend/{campaign_id}")
def recommend(campaign_id: int):
    query = """
        SELECT
    r.normalized_score,
    r.confidence_level,
    i.channel_id,
    i.channel_name,
    i.brand_safety_score,
    c.title AS campaign_title,
    e.explanation
    FROM ranking_scores r
    JOIN influencers i ON r.influencer_id = i.influencer_id
    JOIN campaigns c ON r.campaign_id = c.campaign_id
    LEFT JOIN ranking_explanations e
    ON e.campaign_id = r.campaign_id
    AND e.influencer_id = r.influencer_id
    WHERE r.campaign_id = %s
    ORDER BY r.normalized_score DESC
    LIMIT 10

    """

    cursor.execute(query, (campaign_id,))
    rows = cursor.fetchall()

    if not rows:
        return {
            "campaign_id": campaign_id,
            "recommendations": [],
            "message": "No influencers available yet"
        }
    
    results = []
    for idx, row in enumerate(rows, start=1):
      results.append({
        "rank": idx,
        "score": float(row["normalized_score"]) if row["normalized_score"] else 0.0,
        "confidence": float(row["confidence_level"]) if row["confidence_level"] else 0.0,
        "channel_id": row["channel_id"],
        "channel_name": row["channel_name"],
        "brand_safety_score": float(row["brand_safety_score"]) if row["brand_safety_score"] else 1.0,
        "campaign": row["campaign_title"],
        "why_recommended": row["explanation"] or "Based on AI ranking"
    })

    return {
        "campaign_id": campaign_id,
        "recommendations": results
    }
