from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def comment_quality_score(comments):
    if not comments or len(comments) < 5:
        return 0.3

    embeddings = model.encode(comments)
    sims = []

    for i in range(len(embeddings)-1):
        sim = np.dot(embeddings[i], embeddings[i+1]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1])
        )
        sims.append(sim)

    avg_similarity = sum(sims) / len(sims)

    # High similarity = bot comments
    quality = 1 - avg_similarity
    return round(max(0.0, min(1.0, quality)), 3)
