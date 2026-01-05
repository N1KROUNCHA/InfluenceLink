import numpy as np

def compute_ranking_score(X):
    # Custom learned weights (can later optimize)
    weights = np.array([0.3, 0.2, 0.3, 0.2])
    scores = np.dot(X, weights)
    return scores

