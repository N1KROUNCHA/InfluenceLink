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

from app.api.auth import router as auth_router
from app.api.workflow import router as workflow_router

app = FastAPI(title="InfluenceLink API")

# CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"], # Debug only
    allow_origin_regex="https://.*\.vercel\.app",
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ],
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
app.include_router(auth_router)
app.include_router(workflow_router)


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