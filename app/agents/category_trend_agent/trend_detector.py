from collections import Counter
import math

def detect_trends(texts):
    words = []
    for t in texts:
        words.extend(t.lower().split())

    freq = Counter(words)

    # Remove noise
    common = [w for w, c in freq.items() if c > 3 and len(w) > 4]

    trend_score = {w: math.log(freq[w] + 1) for w in common}

    return sorted(trend_score.items(), key=lambda x: x[1], reverse=True)[:10]
