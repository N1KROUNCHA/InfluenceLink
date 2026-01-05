import numpy as np

def growth_score(time_series):
    if len(time_series) < 5:
        return 0.3

    x = np.arange(len(time_series))
    y = np.array(time_series)

    slope = np.polyfit(x, y, 1)[0]
    return round(max(0.0, min(1.0, slope / max(y))), 3)
