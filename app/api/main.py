from fastapi import FastAPI, Request, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import traceback
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("uvicorn.error")

# Routers
from app.api.campaigns1 import router as campaigns_router
from app.api.content1 import router as content_router
from app.api.influencers import router as influencers_router
from app.api.utils import router as utils_router
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.workflow import router as workflow_router

app = FastAPI(title="InfluenceLink API")

# Add TrustedHostMiddleware to allowing wildcard hosts (prevents 400 Bad Request on Host header)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Manual CORS Middleware to fix persistent 400 Bad Request on OPTIONS
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    try:
        origin = request.headers.get("Origin")
        logger.info(f"DEBUG_CORS: {request.method} request to {request.url} from origin: {origin}")
        
        # Handle Preflight OPTIONS requests directly
        if request.method == "OPTIONS":
            logger.info("DEBUG_CORS: Handling OPTIONS preflight")
            response = Response(status_code=200) # Explicitly set 200
            response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

        # Handle actual request
        response = await call_next(request)
        
        # Add CORS headers to response
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    except Exception as e:
        logger.error(f"CORS_ERROR: {str(e)}")
        # traceback.print_exc()
        # On error, try to pass through
        return await call_next(request)

# Register routers (AFTER app init)
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