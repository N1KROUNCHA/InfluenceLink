from app.db.mysql import cursor, conn

def save_influencer(data):
    cursor.execute("""
        INSERT INTO influencers (
            channel_id,
            channel_name,
            category,
            primary_language,
            region,
            subscriber_count,
            avg_views,
            like_ratio,
            comment_ratio,
            engagement_score,
            authenticity_score,
            style,
            video_count
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            subscriber_count=VALUES(subscriber_count),
            avg_views=VALUES(avg_views),
            engagement_score=VALUES(engagement_score),
            authenticity_score=VALUES(authenticity_score),
            video_count=VALUES(video_count)
    """, (
        data["channel_id"],
        data["channel_name"],
        data["category"],
        data["primary_language"],
        data["region"],
        data["subscriber_count"],
        data["avg_views"],
        data["like_ratio"],
        data["comment_ratio"],
        data["engagement_score"],
        data["authenticity_score"],
        data["style"],
        data["video_count"]
    ))

    conn.commit()
