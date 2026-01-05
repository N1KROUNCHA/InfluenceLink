from fastapi import APIRouter
from app.db.mysql import cursor, conn, lock
from app.db.mongo import db
import requests
import os

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "InfluenceLink API"
    }


@router.get("/detailed")
def detailed_health_check():
    """Detailed health check with database and service status"""
    health_status = {
        "status": "healthy",
        "service": "InfluenceLink API",
        "checks": {}
    }
    
    # Check MySQL connection
    try:
        with lock:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status["checks"]["mysql"] = {
            "status": "healthy",
            "message": "MySQL connection successful"
        }
    except Exception as e:
        health_status["checks"]["mysql"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check MongoDB connection
    try:
        db.command("ping")
        health_status["checks"]["mongodb"] = {
            "status": "healthy",
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        health_status["checks"]["mongodb"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Ollama service
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/tags")
    try:
        response = requests.get(ollama_url, timeout=2)
        if response.status_code == 200:
            health_status["checks"]["ollama"] = {
                "status": "healthy",
                "message": "Ollama service is running"
            }
        else:
            health_status["checks"]["ollama"] = {
                "status": "unhealthy",
                "message": f"Ollama returned status {response.status_code}"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["ollama"] = {
            "status": "unhealthy",
            "message": f"Cannot connect to Ollama: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Get basic stats
    try:
        with lock:
            cursor.execute("SELECT COUNT(*) as count FROM campaigns")
            campaign_count = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM influencers")
            influencer_count = cursor.fetchone()["count"]
        
        health_status["stats"] = {
            "campaigns": campaign_count,
            "influencers": influencer_count
        }
    except Exception as e:
        health_status["stats"] = {
            "error": str(e)
        }
    
    return health_status

