def final_authenticity_score(
    engagement_score,
    comment_score,
    temporal_score
):
    return round(
        0.4 * engagement_score +
        0.35 * comment_score +
        0.25 * temporal_score,
        3
    )
