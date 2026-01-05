import numpy as np

def temporal_consistency_score(view_series):
    if len(view_series) < 5:
        return 0.5

    variance = np.std(view_series)
    mean = np.mean(view_series)

    if mean == 0:
        return 0.2

    score = 1 - (variance / mean)
    return round(max(0.0, min(1.0, score)), 3)
