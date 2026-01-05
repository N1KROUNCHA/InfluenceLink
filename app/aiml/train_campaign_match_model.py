import os
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from app.db.mysql import conn

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


def train_campaign_model():
    df = pd.read_sql("SELECT * FROM campaign_training_data", conn)

    if df.empty:
        print("⚠️ No training rows found — skipping model training.")
        return

    # pseudo-labels (ranking signal)
    df["normalized_score"] = (
        0.30 * df["dna_similarity"].fillna(0)
        + 0.20 * df["topic_overlap"].fillna(0)
        + 0.15 * df["engagement_score"].fillna(0)
        + 0.15 * df["authenticity_score"].fillna(0)
        + 0.10 * df["category_match"].fillna(0)
        + 0.05 * df["style_match"].fillna(0)
        + 0.05 * df["region_match"].fillna(0)
    )

    X = df[FEATURES].fillna(0)
    y = df["normalized_score"]

    if len(X) < 5:
        print("⚠️ Not enough rows to train ML model.")
        return

    model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )

    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("✅ Model trained and saved →", MODEL_PATH)
