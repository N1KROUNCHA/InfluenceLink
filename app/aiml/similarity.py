import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(vec1, vec2):
    """
    Computes cosine similarity between two embeddings.
    Safe against None or empty values.
    """

    if vec1 is None or vec2 is None:
        return 0.0

    try:
        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0][0])
    except Exception:
        return 0.0
