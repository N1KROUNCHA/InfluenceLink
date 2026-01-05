import numpy as np
from app.db.mysql import conn, cursor
from app.aiml.dataset_builder import load_dataset
from app.aiml.preprocess import normalize_features
from app.aiml.ranking_model import compute_ranking_score

MODEL_VERSION = "v1_weighted_rank"

def get_active_campaign_id():
    cursor.execute(
        "SELECT campaign_id FROM campaigns WHERE status='active' LIMIT 1"
    )
    row = cursor.fetchone()
    if not row:
        raise Exception("No active campaign found")
    return row[0]
def get_influencer_ids():
    cursor.execute(
        "SELECT influencer_id FROM influencers ORDER BY influencer_id"
    )
    return [row[0] for row in cursor.fetchall()]

def store_scores():
    campaign_id = get_active_campaign_id()
    print("Using campaign_id:", campaign_id)

    df = load_dataset()
    X = normalize_features(df)
    raw_scores = compute_ranking_score(X)

    min_s, max_s = raw_scores.min(), raw_scores.max()
    normalized_scores = (
        (raw_scores - min_s) / (max_s - min_s)
        if max_s != min_s else raw_scores
    )

    ranks = np.argsort(-normalized_scores) + 1

    influencer_ids = get_influencer_ids()

    if len(influencer_ids) != len(raw_scores):
        raise Exception("Influencer count mismatch between MySQL and AIML data")

    cursor.execute(
        "DELETE FROM ranking_scores WHERE campaign_id=%s",
        (campaign_id,)
    )

    for idx, influencer_id in enumerate(influencer_ids):
        cursor.execute("""
            INSERT INTO ranking_scores
            (campaign_id, influencer_id, model_version,
             raw_score, normalized_score, rank_position, confidence_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            campaign_id,
            influencer_id,
            MODEL_VERSION,
            float(raw_scores[idx]),
            float(normalized_scores[idx]),
            int(ranks[idx]),
            round(float(normalized_scores[idx]), 3)
        ))

    conn.commit()
    print("AIML ranking scores stored successfully")



if __name__ == "__main__":
    store_scores()
