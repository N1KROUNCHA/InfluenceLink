from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.db.mysql import cursor, conn
from app.api.auth import get_current_user

router = APIRouter(prefix="/workflow", tags=["Workflow"])

class WorkflowUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class WorkflowItem(BaseModel):
    influencer_id: int
    channel_name: str
    status: str
    notes: Optional[str]
    updated_at: str

@router.post("/{campaign_id}/add/{influencer_id}")
def add_to_workflow(campaign_id: int, influencer_id: int, current_user = Depends(get_current_user)):
    # Verify campaign ownership (simplified for now, mimicking campaigns1.py check)
    cursor.execute("SELECT brand_id FROM campaigns WHERE campaign_id = %s", (campaign_id,))
    campaign = cursor.fetchone()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # In a real app, check if current_user.brand_id == campaign.brand_id
    
    try:
        cursor.execute("""
            INSERT INTO influencer_workflow (campaign_id, influencer_id, status)
            VALUES (%s, %s, 'shortlisted')
            ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP
        """, (campaign_id, influencer_id))
        conn.commit()
        return {"message": "Influencer added to workflow"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{campaign_id}/update/{influencer_id}")
def update_workflow_status(campaign_id: int, influencer_id: int, data: WorkflowUpdate, current_user = Depends(get_current_user)):
    print(f"DEBUG UPDATE: Camp {campaign_id}, Inf {influencer_id}, Data: {data}")
    try:
        # If notes is None, keep existing notes
        cursor.execute("""
            UPDATE influencer_workflow 
            SET status = %s, notes = COALESCE(%s, notes)
            WHERE campaign_id = %s AND influencer_id = %s
        """, (data.status, data.notes, campaign_id, influencer_id))
        conn.commit()
        conn.commit()
        return {"message": "Status updated", "debug_data": str(data)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{campaign_id}")
def get_campaign_workflow(campaign_id: int, current_user = Depends(get_current_user)):
    query = """
        SELECT 
            w.influencer_id,
            i.channel_name,
            w.status,
            w.notes,
            w.updated_at
        FROM influencer_workflow w
        JOIN influencers i ON w.influencer_id = i.influencer_id
        WHERE w.campaign_id = %s
        ORDER BY w.updated_at DESC
    """
    cursor.execute(query, (campaign_id,))
    rows = cursor.fetchall()
    
    # Group by status for easier frontend consumption
    pipeline = {
        "shortlisted": [],
        "outreached": [],
        "negotiating": [],
        "contracted": [],
        "post_live": [],
        "completed": [],
        "rejected": []
    }
    
    all_ids = []
    for row in rows:
        inf_id = row["influencer_id"]
        all_ids.append(inf_id)
        status = row["status"]
        if status in pipeline:
            pipeline[status].append({
                "influencer_id": inf_id,
                "channel_name": row["channel_name"],
                "notes": row["notes"],
                "updated_at": str(row["updated_at"])
            })
            
    return {
        "pipeline": pipeline,
        "all_ids": all_ids
    }

@router.delete("/{campaign_id}/remove/{influencer_id}")
def remove_from_workflow(campaign_id: int, influencer_id: int, current_user = Depends(get_current_user)):
    try:
        cursor.execute("DELETE FROM influencer_workflow WHERE campaign_id = %s AND influencer_id = %s", (campaign_id, influencer_id))
        conn.commit()
        return {"message": "Removed from workflow"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-collaborations/{influencer_id}")
def get_influencer_workflow(influencer_id: int, current_user = Depends(get_current_user)):
    query = """
        SELECT 
            w.campaign_id,
            c.title as campaign_title,
            b.brand_name,
            w.status,
            w.notes,
            w.updated_at
        FROM influencer_workflow w
        JOIN campaigns c ON w.campaign_id = c.campaign_id
        JOIN brands b ON c.brand_id = b.brand_id
        WHERE w.influencer_id = %s
        ORDER BY w.updated_at DESC
    """
    cursor.execute(query, (influencer_id,))
    rows = cursor.fetchall()
    return rows
