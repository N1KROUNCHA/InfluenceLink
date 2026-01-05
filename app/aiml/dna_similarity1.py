import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load once globally
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


def normalize(vec):
    """Ensure numpy float array"""
    if vec is None or len(vec) == 0:
        return None
    return np.array(vec, dtype="float32").reshape(1, -1)


def compute_dna_similarity(brand_embedding, influencer_embedding):
    """
    Returns similarity score between 0 and 1
    """

    if not brand_embedding or not influencer_embedding:
        return 0.0

    try:
        v1 = normalize(brand_embedding)
        v2 = normalize(influencer_embedding)

        if v1 is None or v2 is None:
            return 0.0

        sim = cosine_similarity(v1, v2)[0][0]

        # clamp to [0,1]
        return float(max(0.0, min(1.0, sim)))

    except Exception as e:
        print("⚠️ similarity error:", e)
        return 0.0
