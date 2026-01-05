import os
import joblib
import pandas as pd
from app.db.mysql import conn, cursor

MODEL_PATH = "models/campaign_rank_model.pkl"

FEATURES = [
    "subscriber_count",
    "avg_views",
    "engagement_score",
    "authenticity_score",
    "dna_similarity",
    "topic_overlap",
    "category_match",
    "style_match",
    "region_match"
]


def predict_campaign_ranking(campaign_id: int):

    if not os.path.exists(MODEL_PATH):
        raise Exception("Model not trained yet")

    model = joblib.load(MODEL_PATH)

    df = pd.read_sql(
        "SELECT * FROM campaign_training_data WHERE campaign_id=%s",
        conn,
        params=(campaign_id,)
    )

    if df.empty:
        raise Exception("No training rows for this campaign")

    X = df[FEATURES].fillna(0)
    scores = model.predict(X)

    df["normalized_score"] = scores
    df = df.sort_values("normalized_score", ascending=False)

    for rank, row in enumerate(df.itertuples(), start=1):
        cursor.execute("""
            INSERT INTO ranking_scores
            (campaign_id, influencer_id, normalized_score, confidence_level, rank_position)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              normalized_score=VALUES(normalized_score),
              confidence_level=VALUES(confidence_level),
              rank_position=VALUES(rank_position)
        """, (
            row.campaign_id,
            row.influencer_id,
            float(row.normalized_score),
            min(1.0, float(row.normalized_score)),
            rank
        ))

    conn.commit()
    print("✅ Rankings generated successfully")
