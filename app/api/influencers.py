from fastapi import APIRouter, HTTPException
from app.db.mysql import cursor, conn
from app.db.mongo import db
from app.aiml.faiss_search import search_similar

router = APIRouter(prefix="/influencers", tags=["Influencers"])


@router.get("/search")
def search_influencers(
    category: str = None,
    min_subscribers: int = None,
    max_subscribers: int = None,
    min_engagement: float = None,
    limit: int = 20
):
    """Search influencers with filters"""
    conditions = []
    params = []
    
    if category:
        conditions.append("(category LIKE %s OR channel_name LIKE %s)")
        params.append(f"%{category}%")
        params.append(f"%{category}%")
    
    if min_subscribers:
        conditions.append("subscriber_count >= %s")
        params.append(min_subscribers)
    
    if max_subscribers:
        conditions.append("subscriber_count <= %s")
        params.append(max_subscribers)
    
    if min_engagement:
        conditions.append("engagement_score >= %s")
        params.append(min_engagement)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    params.append(limit)
    
    query = f"""
        SELECT influencer_id, channel_id, channel_name, category,
               subscriber_count, engagement_score, brand_safety_score
        FROM influencers
        WHERE {where_clause}
        ORDER BY subscriber_count DESC
        LIMIT %s
    """
    
    cursor.execute(query, tuple(params))
    influencers = cursor.fetchall()
    
    return {
        "count": len(influencers),
        "influencers": influencers
    }


@router.get("/channel/{channel_id}")
def get_influencer_by_channel(channel_id: str):
    """Get influencer by channel ID"""
    cursor.execute("""
        SELECT *
        FROM influencers
        WHERE channel_id = %s
    """, (channel_id.strip(),))
    
    influencer = cursor.fetchone()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")
    
    # Get DNA data
    influencer_id = influencer["influencer_id"]
    dna_doc = db.influencer_dna.find_one({"influencer_id": influencer_id})
    
    result = dict(influencer)
    if dna_doc:
        result["dna"] = {
            "topics": dna_doc.get("topics", []),
            "style": dna_doc.get("style", ""),
            "has_embedding": "embedding" in dna_doc
        }
    
    return result


@router.get("/find_similar/{channel_id}")
def find_similar_influencers(channel_id: str, top_k: int = 10):
    # Strip any whitespace from the channel_id
    channel_id = channel_id.strip()
    # 1. Find the influencer_id from the channel_id
    cursor.execute("SELECT influencer_id FROM influencers WHERE channel_id = %s", (channel_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Influencer not found")
    
    influencer_id = row["influencer_id"]

    # 2. Get the influencer's DNA embedding from MongoDB
    dna_doc = db.influencer_dna.find_one({"influencer_id": influencer_id})
    if not dna_doc or "embedding" not in dna_doc:
        # Instead of error, return empty similar list
        return {"seed_influencer": channel_id, "similar_influencers": []}
    
    query_embedding = dna_doc["embedding"]

    # 3. Use FAISS to find similar influencers
    similar_influencers_data = search_similar(query_embedding, top_k=top_k + 1) # +1 to exclude the influencer itself

    # 4. Fetch details for the similar influencers
    similar_ids = [
        influencer["influencer_id"]
        for influencer in similar_influencers_data
        if influencer["influencer_id"] != influencer_id
    ]

    if not similar_ids:
        return {"influencer_id": influencer_id, "similar_influencers": []}

    # Use a placeholder for each ID in the IN clause
    placeholders = ','.join(['%s'] * len(similar_ids))
    query = f"""
        SELECT influencer_id, channel_id, channel_name, category, subscriber_count, engagement_score
        FROM influencers
        WHERE influencer_id IN ({placeholders})
    """
    
    cursor.execute(query, tuple(similar_ids))
    similar_influencer_rows = cursor.fetchall()

    # Create a map of influencer_id to its similarity score
    similarity_map = {item['influencer_id']: item['similarity'] for item in similar_influencers_data}

    results = []
    for row in similar_influencer_rows:
        current_influencer_id = row["influencer_id"]
        results.append({
            "channel_id": row["channel_id"],
            "channel_name": row["channel_name"],
            "category": row["category"],
            "subscriber_count": row["subscriber_count"],
            "engagement_score": row["engagement_score"],
            "similarity": similarity_map.get(current_influencer_id)
        })

    # Sort results by similarity score
    results.sort(key=lambda x: x["similarity"], reverse=True)

    return {"seed_influencer": channel_id, "similar_influencers": results}


@router.get("/{influencer_id}")
def get_influencer(influencer_id: int):
    """Get detailed influencer information"""
    cursor.execute("""
        SELECT *
        FROM influencers
        WHERE influencer_id = %s
    """, (influencer_id,))
    
    influencer = cursor.fetchone()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")
    
    # Get DNA data from MongoDB
    dna_doc = db.influencer_dna.find_one({"influencer_id": influencer_id})
    
    result = dict(influencer)
    if dna_doc:
        result["dna"] = {
            "topics": dna_doc.get("topics", []),
            "style": dna_doc.get("style", ""),
            "has_embedding": "embedding" in dna_doc
        }
    
    return result

@router.get("/{influencer_id}/roi")
def get_roi_prediction(influencer_id: int):
    """Predict performance (views) for an influencer"""
    cursor.execute("SELECT subscriber_count, engagement_score FROM influencers WHERE influencer_id=%s", (influencer_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Influencer not found")
        
    from app.aiml.roi_model import predict_performance, train_roi_model
    import os
    
    # Train if needed
    if not os.path.exists("models/roi_model.pkl"):
        train_roi_model()
        
    prediction = predict_performance(row["subscriber_count"], row["engagement_score"])
    
    return prediction
