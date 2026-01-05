import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def compute_dna_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0

    try:
        a = np.array(vec1).reshape(1, -1)
        b = np.array(vec2).reshape(1, -1)
        return float(cosine_similarity(a, b)[0][0])
    except:
        return 0.0
