import pandas as pd
import joblib
import os
from app.db.mysql import conn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

MODEL_PATH = "models/campaign_rank_model.pkl"
METRICS_PATH = "models/model_metrics.joblib"

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
    print("🚂 Starting ML Model Training...")
    
    # 1. Load Data
    df = pd.read_sql("SELECT * FROM campaign_training_data WHERE quality_score IS NOT NULL", conn)

    if len(df) < 50:
        print(f"⚠️ Not enough data ({len(df)} rows). Need at least 50 for training.")
        return

    # 2. Preprocessing
    X = df[FEATURES].fillna(0)
    y = df["quality_score"]

    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Model Definition & Training
    print(f"📊 Training on {len(X_train)} samples, testing on {len(X_test)} samples...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # 5. Evaluation
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"✅ Model Trained!")
    print(f"📈 Performance - MSE: {mse:.4f}, R2 Score: {r2:.4f}")

    # 6. Feature Importance
    importances = model.feature_importances_
    feat_importances = pd.Series(importances, index=FEATURES).sort_values(ascending=False)
    print("\n💡 Feature Importance Ranking:")
    print(feat_importances)

    # 7. Save Model & Metrics
    if not os.path.exists("models"):
        os.makedirs("models")
        
    joblib.dump(model, MODEL_PATH)
    joblib.dump({
        "mse": mse,
        "r2": r2,
        "feature_importances": feat_importances.to_dict(),
        "n_samples": len(df)
    }, METRICS_PATH)
    
    print(f"💾 Saved model to {MODEL_PATH}")

if __name__ == "__main__":
    train_campaign_model()
