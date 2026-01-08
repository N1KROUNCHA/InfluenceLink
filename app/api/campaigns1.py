from fastapi import APIRouter, HTTPException, Depends
from app.db.mysql import cursor, conn, lock
from app.agents.brand_dna.brand_dna_builder import build_brand_dna
from app.aiml.build_campaign_training_data1 import build_campaign_training_data
from app.aiml.train_campaign_match_model1 import train_campaign_model
from app.aiml.predict_campaign_ranking1 import predict_campaign_ranking
from app.api.auth import get_current_user
from fastapi import BackgroundTasks

from fastapi import APIRouter, HTTPException, Depends
from app.api.auth import get_current_user
from fastapi import BackgroundTasks

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

def run_campaign_ai(campaign_id: int, data: dict):
    """Background task to run AI analysis for a campaign"""
    print(f"🤖 [AI] Starting analysis for Campaign {campaign_id}")
    try:
        # 1. Build DNA (Embedding)
        # We need to ensure 'campaign_id' is in data for the builder
        data["campaign_id"] = campaign_id
        build_brand_dna(data)
        print(f"✅ [AI] DNA Built for Campaign {campaign_id}")
        
        # 2. Predict / Rank Influencers
        # This will use the DNA we just built to find similar influencers via vector search (cold start)
        # or use the trained model if we have data.
        results = predict_campaign_ranking(campaign_id)
        print(f"✅ [AI] Ranking Complete. Found {len(results)} matches.")
        
    except Exception as e:
        print(f"❌ [AI Error] Campaign {campaign_id}: {e}")
        import traceback
        traceback.print_exc()

# Deprecated or simple create endpoint - let's secure it too if used, 
# but the main one seems to be the one below with BackgroundTasks.
# We will consolidate or just fix the used ones. 
# The one at line 54 (@router.post("/create")) is likely the one used by frontend.

@router.post("/create")
def create_campaign(data: dict, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    
    if current_user["type"] != "brand":
         raise HTTPException(status_code=403, detail="Only brands can create campaigns")

    brand_id = current_user["user_id"]

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
        brand_id,
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
def trigger_ranking(campaign_id: int, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Manually trigger AI ranking"""
    # Fetch campaign data first to pass to DNA builder if needed
    # Also verify ownership
    cursor.execute("SELECT * FROM campaigns WHERE campaign_id=%s", (campaign_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check ownership (Bypass for Admin)
    is_admin = current_user.get("email") == "srinidhikrouncha1956@gmail.com"
    if not is_admin and current_user["type"] == "brand" and row["brand_id"] != current_user["user_id"]:
         raise HTTPException(status_code=403, detail="Not authorized")

    data = {
        "campaign_name": row["title"],
        "category": row["category"],
        "target_region": row["target_region"],
        "required_style": row["required_style"]
    }
    
    background_tasks.add_task(run_campaign_ai, campaign_id, data)
    return {"message": "AI Ranking started in background"}


@router.get("/list")
def list_campaigns(status: str = None, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """List campaigns for the current user"""
    with lock:
        # Special Admin Access for specific user
        if current_user.get("email") == "srinidhikrouncha1956@gmail.com":
             # Show ALL campaigns for this super-user/admin
             query = "SELECT campaign_id, title, category, status, budget, created_at FROM campaigns WHERE 1=1"
             params = []
        elif current_user["type"] == "brand":
             # Strict isolation for other brands
             query = "SELECT campaign_id, title, category, status, budget, created_at FROM campaigns WHERE brand_id = %s"
             params = [current_user["user_id"]]
        else:
             # Influencer view
             query = "SELECT campaign_id, title, category, status, budget, created_at FROM campaigns WHERE status = 'active'"
             params = []

        if status:
            query += " AND status = %s"
            params.append(status)
            
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
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


@router.get("/{campaign_id}/model-insights")
def get_model_insights(campaign_id: int):
    """Expose ML model performance and feature metrics for faculty project"""
    import joblib
    import os
    
    METRICS_PATH = "models/model_metrics.joblib"
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="Model metrics not yet generated. Please trigger a ranking first.")
        
    metrics = joblib.load(METRICS_PATH)
    
    # Check if this campaign has specific explanations
    cursor.execute("""
        SELECT i.channel_name, e.explanation, r.normalized_score
        FROM ranking_explanations e
        JOIN influencers i ON e.influencer_id = i.influencer_id
        JOIN ranking_scores r ON (e.campaign_id = r.campaign_id AND e.influencer_id = r.influencer_id)
        WHERE e.campaign_id = %s
        ORDER BY r.normalized_score DESC
        LIMIT 5
    """, (campaign_id,))
    top_explanations = cursor.fetchall()

    return {
        "model_type": "RandomForestRegressor (Scikit-Learn)",
        "evaluation_metrics": {
            "mean_squared_error": float(metrics["mse"]),
            "r2_score": float(metrics["r2"]),
            "total_training_samples": metrics["n_samples"]
        },
        "feature_importance": metrics["feature_importances"],
        "top_match_explanations": [
            {
                "influencer": row["channel_name"],
                "score": float(row["normalized_score"]),
                "ai_reason": row["explanation"]
            }
            for row in top_explanations
        ]
    }

@router.get("/recommend/{campaign_id}")
def recommend(campaign_id: int):
    query = """
    SELECT 
    r.influencer_id,
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
    LIMIT 15
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
      # Cap score at 1.0 (100%) for UI sanity
      raw_score = float(row["normalized_score"]) if row["normalized_score"] else 0.0
      capped_score = min(1.0, raw_score)
      
      results.append({
        "rank": idx,
        "influencer_id": row["influencer_id"],
        "score": capped_score,
        "confidence": float(row["confidence_level"]) if row["confidence_level"] else 0.9,
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
