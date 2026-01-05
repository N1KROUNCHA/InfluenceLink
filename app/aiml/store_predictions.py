import joblib
import pandas as pd
from app.db.mysql import conn, cursor

MODEL_PATH = "app/aiml/influencer_model.pkl"

def store_predictions(campaign_id=2):
    model = joblib.load(MODEL_PATH)

    query = """
    SELECT influencer_id,
           subscriber_count,
           video_count,
           avg_views
    FROM influencers
    WHERE avg_views IS NOT NULL
    """

    df = pd.read_sql(query, conn)

    X = df.drop(columns=["influencer_id"])
    predictions = model.predict(X)

    # Normalize scores (0–1)
    min_s, max_s = predictions.min(), predictions.max()
    norm_scores = (predictions - min_s) / (max_s - min_s + 1e-6)

    for i, row in df.iterrows():
        cursor.execute("""
    INSERT INTO ranking_scores (
        campaign_id,
        influencer_id,
        model_version,
        raw_score,
        normalized_score,
        confidence_level
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        raw_score = VALUES(raw_score),
        normalized_score = VALUES(normalized_score),
        model_version = VALUES(model_version),
        confidence_level = VALUES(confidence_level),
        created_at = CURRENT_TIMESTAMP
""", (
    campaign_id,
    int(row["influencer_id"]),
    "LinearRegression-v1",
    float(predictions[i]),
    float(norm_scores[i]),
    0.85
))


    conn.commit()
    print("AIML predictions stored successfully")


if __name__ == "__main__":
    store_predictions()
