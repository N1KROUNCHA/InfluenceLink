from sentence_transformers import SentenceTransformer
from app.db.mongo import db
import numpy as np

# Load model once
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def build_influencer_dna(influencer_data):
    """
    Generates DNA embedding for an influencer based on their textual data.
    Updates MongoDB 'influencer_dna' collection.
    """
    channel_id = influencer_data["channel_id"]
    channel_name = influencer_data["channel_name"]
    description = influencer_data.get("description", "")
    category = influencer_data.get("category", "") or ""
    style = influencer_data.get("style", "") or ""
    
    # Construct distinct text representation
    # Weighting certain parts by repeating or structuring? 
    # For now, simple concatenation.
    text_corpus = f"{channel_name}. Category: {category}. Style: {style}. {description}"
    
    print(f"🧬 Generating DNA for {channel_name}...")
    
    embedding = model.encode(text_corpus).tolist()
    
    # Extract keywords/topics (simple heuristic or use keywords if available)
    # For now, we reuse existing topics if present or empty
    topics = influencer_data.get("topics", [])
    if not topics and category:
        topics = [category]

    # Update/Insert into MongoDB
    dna_doc = {
        "influencer_id": influencer_data.get("influencer_id"), # Might be None if not passed, key is channel_id usually
        "channel_id": channel_id,
        "embedding": embedding,
        "topics": topics,
        "style": style,
        "last_updated": np.datetime64('now').astype(str)
    }
    
    # Using upsert on channel_id
    db.influencer_dna.update_one(
        {"channel_id": channel_id},
        {"$set": dna_doc},
        upsert=True
    )
    
    print(f"✅ DNA Generated for {channel_name}")
    return embedding
