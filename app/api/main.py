from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.mysql import cursor
from fastapi import HTTPException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Routers
from app.api.campaigns1 import router as campaigns_router
from app.api.content1 import router as content_router
from app.api.influencers import router as influencers_router
from app.api.utils import router as utils_router
from app.api.health import router as health_router

app = FastAPI(title="InfluenceLink API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(campaigns_router)
app.include_router(content_router)
app.include_router(influencers_router)
app.include_router(utils_router)
app.include_router(health_router)


@app.get("/")
def root():
    return {"status": "InfluenceLink backend running"}


@app.get("/recommend/{campaign_id}")
def recommend_influencers(campaign_id: int):
    query = """
        SELECT
    r.normalized_score,
    r.confidence_level,
    i.channel_id,
    i.channel_name,
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
        raise HTTPException(status_code=404, detail="No recommendations found")

    results = []
    for idx, row in enumerate(rows, start=1):
      results.append({
    "rank": idx,
    "score": float(row[0]) if row[0] else 0.0,
    "confidence": float(row[1]) if row[1] else 0.0,
    "channel_id": row[2],
    "channel_name": row[3],
    "campaign": row[4],
    "why_recommended": row[5] or "Based on AI ranking"
})



    return {
        "campaign_id": campaign_id,
        "recommendations": results
    }
@app.get("/")
def root():
    return {
        "message": "InfluenceLink API is running",
        "endpoints": [
            "/campaigns/create",
            "/recommend/{campaign_id}",
            "/docs"
        ]
    }