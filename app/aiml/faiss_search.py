import faiss
import numpy as np
import os
from app.db.mongo import db

INDEX_PATH = "models/influencer_faiss.index"


def search_similar(query_embedding, top_k=300):
    if not os.path.exists(INDEX_PATH):
        raise Exception("FAISS index not found. Run build_faiss_index first.")

    index = faiss.read_index(INDEX_PATH)

    query = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query, top_k)

    results = []

    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1:
            continue

        doc = db.influencer_dna.find_one({"faiss_id": int(idx)})
        if not doc:
            continue

        results.append({
            "influencer_id": doc["influencer_id"],
            # convert distance → similarity
            "similarity": float(1 / (1 + dist))
        })

    return results
