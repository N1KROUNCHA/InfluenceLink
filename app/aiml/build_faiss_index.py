import faiss
import numpy as np
from app.db.mongo import db
import os

INDEX_PATH = "models/influencer_faiss.index"

def build_faiss_index():
    print("🔧 Building FAISS index...")

    docs = list(db.influencer_dna.find({
        "embedding": {"$exists": True, "$ne": []}
    }))

    if not docs:
        raise Exception("❌ No influencer embeddings found")

    vectors = []
    id_map = []

    for i, doc in enumerate(docs):
        emb = doc.get("embedding")
        if not emb:
            continue

        vectors.append(emb)
        # 🔥 FIX: Ensure influencer_id exists before appending
        influencer_id = doc.get("influencer_id")
        if influencer_id is None:
            continue
        id_map.append(influencer_id)

        # Save mapping
        db.influencer_dna.update_one(
            {"_id": doc["_id"]},
            {"$set": {"faiss_id": i}}
        )

    X = np.array(vectors).astype("float32")

    dim = X.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(X)

    os.makedirs("models", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    print(f"✅ FAISS index built with {len(X)} influencers")


# 🔥 THIS IS WHAT YOU WERE MISSING
if __name__ == "__main__":
    build_faiss_index()
