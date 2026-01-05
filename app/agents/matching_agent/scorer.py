import numpy as np

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def final_score(similarity, engagement, authenticity):
    """
    Weighted scoring
    """
    return (
        0.6 * similarity +
        0.25 * engagement +
        0.15 * authenticity
    )
