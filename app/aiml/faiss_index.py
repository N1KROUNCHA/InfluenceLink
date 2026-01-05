import faiss
import numpy as np
from app.db.mongo import db
import os
import pickle

INDEX_PATH = "models/influencer_faiss.index"
META_PATH = "models/influencer_faiss_meta.pkl"
EMBEDDING_DIM = 384


def build_faiss_index():
    influencers = list(db.influencer_dna.find({}))

    if not influencers:
        raise Exception("No influencer DNA found")

    embeddings = []
    ids = []

    for doc in influencers:
        emb = doc.get("embedding")
        if not emb or len(emb) != EMBEDDING_DIM:
            continue

        embeddings.append(emb)
        ids.append(doc["influencer_id"])

    vectors = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    faiss.normalize_L2(vectors)
    index.add(vectors)

    os.makedirs("models", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(ids, f)

    print(f"✅ FAISS index built with {len(ids)} influencers")
