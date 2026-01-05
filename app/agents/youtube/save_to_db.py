from app.db.mysql import cursor, conn


def save_influencers(channels):
    inserted = 0

    for ch in channels:
        cursor.execute("""
            INSERT INTO influencers (
                channel_id,
                channel_name,
                category,
                region,
                primary_language,
                subscriber_count,
                video_count
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                channel_name=VALUES(channel_name),
                category=VALUES(category),
                region=VALUES(region),
                primary_language=VALUES(primary_language),
                subscriber_count=VALUES(subscriber_count),
                video_count=VALUES(video_count)
        """, (
            ch["channel_id"],
            ch["channel_name"],
            ch.get("category"),
            ch.get("region"),
            ch.get("language"),
            ch.get("subscriber_count"),
            ch.get("video_count"),
        ))

        inserted += 1

    conn.commit()
    return inserted
