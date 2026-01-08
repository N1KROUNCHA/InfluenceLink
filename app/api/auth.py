from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from app.db.mysql import cursor, conn
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

from fastapi.security import OAuth2PasswordBearer

# ... existing code ...
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # print(f"DEBUG: Received token: {token}")
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            print("❌ Invalid Token: sub is None")
            raise credentials_exception
            
        user_id = int(user_id_str) # Convert back to int
        user_type: str = payload.get("type")
        email: str = payload.get("email")
        
        return {
            "user_id": user_id, 
            "type": user_type, 
            "name": payload.get("name"),
            "email": email 
        }
    except jwt.ExpiredSignatureError:
        print("❌ Token Expired")
        raise HTTPException(status_code=401, detail="Token Expired")
    except jwt.JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception

class RegisterModel(BaseModel):
    email: str
    password: str
    name: str # Brand Name or Influencer Name
    type: str = "brand" # 'brand' or 'influencer'
    # Optional fields for brand
    website: str = None
    industry: str = None
    # Optional fields for influencer
    youtube_handle: str = None 

class LoginModel(BaseModel):
    email: str
    password: str
    type: str = "brand"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
def register(data: RegisterModel):
    try:
        # 1. Check if user exists
        table = "brands" if data.type == "brand" else "influencers"
        cursor.execute(f"SELECT email FROM {table} WHERE email = %s", (data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_pw = get_password_hash(data.password)
        
        if data.type == "brand":
            cursor.execute("""
                INSERT INTO brands (brand_name, email, password_hash, website, industry, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (data.name, data.email, hashed_pw, data.website or "", data.industry or "General"))
            user_id = cursor.lastrowid
        else:
            # For influencers, we create a basic record first. 
            # Detailed onboarding (YouTube ingest) happens later or via separate call
            cursor.execute("""
                INSERT INTO influencers (channel_name, email, password_hash, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (data.name, data.email, hashed_pw))
            user_id = cursor.lastrowid
            
        conn.commit()
        
        return {"message": "Registration successful", "user_id": user_id, "type": data.type}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Registration Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(data: LoginModel):
    try:
        table = "brands" if data.type == "brand" else "influencers"
        id_col = "brand_id" if data.type == "brand" else "influencer_id"
        name_col = "brand_name" if data.type == "brand" else "channel_name" # Influencer uses channel_name as name
        
        print(f"🔍 Attempting login for {data.email} as {data.type}")
        
        cursor.execute(f"SELECT {id_col}, {name_col}, password_hash FROM {table} WHERE email = %s", (data.email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User not found: {data.email}")
            raise HTTPException(status_code=401, detail="User not found")
            
        if not verify_password(data.password, user["password_hash"]):
             print(f"❌ Password mismatch for {data.email}")
             # Temporary: Detailed error for debugging
             raise HTTPException(status_code=401, detail="Password mismatch")
             
        access_token = create_access_token(
            data={
                "sub": str(user[id_col]), # Convert ID to string for JWT compliance
                "type": data.type, 
                "name": user[name_col],
                "email": data.email
            }
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": user[id_col],
                "name": user[name_col],
                "type": data.type,
                "email": data.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login Error: {e}")
        import traceback
        traceback.print_exc()
        # DEV ONLY: Return error detail
        raise HTTPException(status_code=500, detail="Login failed")

class OnboardModel(BaseModel):
    user_id: int
    youtube_handle: str

@router.post("/influencer/onboard")
def onboard_influencer(data: OnboardModel, background_tasks: BackgroundTasks):
    try:
        from app.youtube.fetch_youtube_influencers import search_channels, get_channel_details
        from app.youtube.normalize_channel import normalize_channel
        from app.youtube.save_influencers import save_influencer
        from app.db.mongo import db
        from app.aiml.build_influencer_dna import build_influencer_dna
        from app.aiml.build_faiss_index import build_faiss_index
        
        # ... (lines 184-263 remain same)
        # 1. Search for channel to get ID
        results = search_channels(data.youtube_handle, max_results=1)
        if not results:
             raise HTTPException(status_code=404, detail="YouTube channel not found")
        
        channel_id = results[0]["snippet"]["channelId"]
        
        # 2. Get full details
        items = get_channel_details([channel_id])
        if not items:
             raise HTTPException(status_code=404, detail="Channel details not found")
             
        raw_data = items[0]
        
        # 3. Normalize
        influencer_data = normalize_channel(raw_data)
        
        # 4. Save to MySQL (Upsert)
        normalized = influencer_data
        cursor.execute("""
            UPDATE influencers SET
                channel_id=%s,
                channel_name=%s,
                subscriber_count=%s,
                avg_views=%s,
                engagement_score=%s,
                authenticity_score=%s,
                video_count=%s,
                description=%s,
                category=%s,
                style = IFNULL(style, 'Informative') -- default style
            WHERE influencer_id=%s
        """, (
            normalized["channel_id"],
            normalized["channel_name"],
            normalized["subscriber_count"],
            normalized["avg_views"],
            normalized["engagement_score"],
            normalized["authenticity_score"],
            normalized["video_count"],
            normalized.get("description", ""),
            normalized.get("category", "General"),
            data.user_id
        ))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
            
        # 5. Insert to MongoDB (Full Data) & Generate DNA
        db.influencers_full.update_one(
            {"channel_id": normalized["channel_id"]}, 
            {"$set": raw_data}, 
            upsert=True
        )
        
        # Trigger DNA generation
        normalized["influencer_id"] = data.user_id
        build_influencer_dna(normalized)
        
        # 🔥 Trigger FAISS Index Rebuild to generate faiss_id
        # We run this as a background task since it can take a few seconds
        background_tasks.add_task(build_faiss_index)
        
        print(f"✅ Onboarded channel {normalized['channel_name']} for user {data.user_id}")
        print(f"⏳ FAISS index rebuild triggered in background")
        
        return {"message": "Onboarding successful", "channel": normalized["channel_name"]}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
def get_profile(current_user = Depends(get_current_user)):
    try:
        if current_user["type"] == "brand":
            cursor.execute("SELECT brand_name, email, industry, website, created_at FROM brands WHERE brand_id = %s", (current_user["user_id"],))
            brand = cursor.fetchone()
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")
            return {
                "user": current_user,
                "domain_details": {
                    "brand_name": brand["brand_name"],
                    "industry": brand["industry"],
                    "website": brand["website"],
                    "joined": str(brand["created_at"])
                }
            }
        else:
            cursor.execute("SELECT channel_name, category, description, created_at FROM influencers WHERE influencer_id = %s", (current_user["user_id"],))
            influencer = cursor.fetchone()
            return {
                "user": current_user, 
                "domain_details": {
                    "channel_name": influencer["channel_name"],
                    "category": influencer["category"],
                    "description": influencer["description"],
                    "joined": str(influencer["created_at"])
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class InfluencerProfileUpdate(BaseModel):
    channel_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

@router.put("/influencer/profile")
def update_influencer_profile(data: InfluencerProfileUpdate, current_user = Depends(get_current_user)):
    if current_user["type"] != "influencer":
        raise HTTPException(status_code=403, detail="Only influencers can update this profile")
    
    try:
        cursor.execute("""
            UPDATE influencers SET
                channel_name = COALESCE(%s, channel_name),
                category = COALESCE(%s, category),
                description = COALESCE(%s, description)
            WHERE influencer_id = %s
        """, (data.channel_name, data.category, data.description, current_user["user_id"]))
        conn.commit()
        return {"message": "Profile updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
