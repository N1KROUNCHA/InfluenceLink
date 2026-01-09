import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from app.db.mysql import conn

MODEL_PATH = "models/roi_model.pkl"
ENCODERS_PATH = "models/roi_encoders.joblib"
METRICS_PATH = "models/roi_metrics.joblib"

def train_roi_model():
    print("🧠 [ML] Training Advanced ROI Predictor (Gradient Boosting)...")
    
    # 1. Fetch training data with more features
    query = """
        SELECT subscriber_count, engagement_score, category, region, authenticity_score, avg_views 
        FROM influencers 
        WHERE avg_views > 0 AND subscriber_count > 0
    """
    df = pd.read_sql(query, conn)
    
    if len(df) < 50:
        print(f"⚠️ Not enough data ({len(df)} rows) to train advanced ROI model")
        return

    # 2. Preprocessing & Encoding
    # Log-scale subscriber count (critical for long-tail distributions)
    df["log_subscribers"] = np.log1p(df["subscriber_count"])
    
    # Encode categorical variables
    encoders = {}
    for col in ["category", "region"]:
        le = LabelEncoder()
        df[col] = df[col].fillna("unknown")
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    # 3. Features & Target
    FEATURES = ["log_subscribers", "engagement_score", "category", "region", "authenticity_score"]
    X = df[FEATURES].fillna(0)
    y = df["avg_views"] # Predicting raw views
    
    # 4. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 5. Model Definition
    # Gradient Boosting is generally superior to Random Forest for structured data
    model = GradientBoostingRegressor(
        n_estimators=200, 
        learning_rate=0.1, 
        max_depth=5, 
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # 6. Evaluation
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"✅ ROI Model Trained! R2 Score: {r2:.4f}, MSE: {mse:.0f}")

    # 7. Save Everything
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    joblib.dump({
        "r2": r2,
        "mse": mse,
        "features": FEATURES,
        "n_samples": len(df)
    }, METRICS_PATH)
    
    print("💾 ROI Model and Meta-data saved!")

def predict_performance(influencer_data: dict):
    """
    Predicts views based on influencer meta-data
    influencer_data should contain: subscriber_count, engagement_score, category, region, authenticity_score
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODERS_PATH):
        # Fallback to smart heuristic
        subs = influencer_data.get("subscriber_count", 0)
        eng = influencer_data.get("engagement_score", 0.05)
        est = subs * (eng * 2) # Heuristic: view rate is roughly double engagement rate
        return {"estimated_views": int(est), "confidence": "heuristic (model missing)"}
        
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    
    # Preprocess input
    log_subs = np.log1p(influencer_data.get("subscriber_count", 0))
    eng = influencer_data.get("engagement_score", 0)
    auth = influencer_data.get("authenticity_score", 0.8)
    
    # Encode categories
    cat_val = influencer_data.get("category", "unknown")
    reg_val = influencer_data.get("region", "unknown")
    
    # Helper for safe encoding
    def safe_transform(encoder, value, default_value="unknown"):
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        if default_value in encoder.classes_:
            return encoder.transform([default_value])[0]
        # Extreme fallback: use the first known class (to prevent crash)
        return encoder.transform([encoder.classes_[0]])[0]

    # Handle unseen labels for encoders
    cat_encoded = safe_transform(encoders["category"], cat_val)
    reg_encoded = safe_transform(encoders["region"], reg_val)

    # Predict
    FEATURES = ["log_subscribers", "engagement_score", "category", "region", "authenticity_score"]
    input_df = pd.DataFrame([[log_subs, eng, cat_encoded, reg_encoded, auth]], columns=FEATURES)
    
    pred_views = model.predict(input_df)[0]
    
    # 7. Implement "Sanity Floor"
    # Even if historical data is zero, an active channel has *some* reach.
    # We use 1% of sub count as a conservative baseline, or 500 views minimum.
    subs = influencer_data.get("subscriber_count", 0)
    floor = max(500, int(subs * 0.01))
    final_views = max(floor, int(pred_views))
    
    return {
        "estimated_views": final_views,
        "confidence": "high (gradient_boosting_ml)"
    }

if __name__ == "__main__":
    train_roi_model()

