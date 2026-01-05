def authenticity_score(subs, avg_views, comment_ratio):
    score = 100

    if avg_views < subs * 0.01:
        score -= 30
    if comment_ratio < 0.002:
        score -= 20

    risk = "low"
    if score < 60:
        risk = "high"

    return {
        "authenticity_score": score,
        "risk_level": risk,
        "flags": []
    }
