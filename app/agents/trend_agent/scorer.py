def trend_score(time_score, topic_score, activity_score):
    return round(
        0.4 * time_score +
        0.35 * topic_score +
        0.25 * activity_score,
        3
    )
