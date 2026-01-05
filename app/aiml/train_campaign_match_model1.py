import pandas as pd
import joblib
from app.db.mysql import conn
from sklearn.ensemble import RandomForestRegressor

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

    if len(df) < 5:
        print("⚠️ Not enough rows to train ML model.")
        return

    X = df[FEATURES].fillna(0)

    # weak supervision label
    y = (
        df["engagement_score"].fillna(0)
        + df["dna_similarity"].fillna(0)
        + df["topic_overlap"].fillna(0)
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("✅ Model trained & saved")
