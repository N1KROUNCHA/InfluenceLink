from fastapi import APIRouter
from app.aiml.build_faiss_index import build_faiss_index

router = APIRouter(prefix="/utils", tags=["Utilities"])

@router.post("/rebuild_index")
def rebuild_index():
    """
    Rebuilds the FAISS index from the latest influencer DNA data.
    """
    try:
        result = build_faiss_index()
        return {"message": "FAISS index rebuilt successfully", "details": result}
    except Exception as e:
        return {"message": "Failed to rebuild FAISS index", "error": str(e)}

