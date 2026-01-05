import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from app.db.mysql import conn

MODEL_PATH = "models/campaign_rank_model.pkl"

FEATURES = [
    "subscriber_count",
    "avg_views",
    "engagement_score",
    "authenticity_score",
    "dna_similarity",
    "category_match",
    "style_match",
    "region_match",
    "trend_alignment_score"
]

TARGET = "normalized_score"


def train_campaign_rank_model():
    print("🧠 Loading campaign training data")

    query = """
        SELECT
            subscriber_count,
            avg_views,
            engagement_score,
            authenticity_score,
            dna_similarity,
            topic_overlap,
            category_match,
            style_match,
            region_match,
            trend_alignment_score,
            normalized_score
        FROM campaign_training_data
        where campaign_id IS NOT NULL
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        print("❌ No training data found")
        return

    X = df[FEATURES].fillna(0)
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)

    joblib.dump(model, MODEL_PATH)

    print("✅ Campaign Rank Model Trained")
    print(f"📉 MAE: {mae:.4f}")
    print(f"💾 Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_campaign_rank_model()
