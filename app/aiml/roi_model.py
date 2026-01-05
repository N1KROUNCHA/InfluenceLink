import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os
from app.db.mysql import conn

MODEL_PATH = "models/roi_model.pkl"

def train_roi_model():
    print("🧠 Training ROI Predictor Model...")
    
    # 1. Fetch training data (Influencers)
    # We use subscriber_count + engagement_score to predict avg_views
    df = pd.read_sql("""
        SELECT subscriber_count, engagement_score, avg_views 
        FROM influencers 
        WHERE avg_views > 0 AND subscriber_count > 0
    """, conn)
    
    if len(df) < 10:
        print("⚠️ Not enough data to train ROI model")
        return

    # 2. Features & Target
    X = df[["subscriber_count", "engagement_score"]]
    y = df["avg_views"]
    
    # 3. Train Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 4. Save Model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("✅ ROI Model trained and saved!")

def predict_performance(subscriber_count, engagement_score):
    if not os.path.exists(MODEL_PATH):
        # Fallback: simple heuristic if model missing
        # 10% view rate avg
        est_views = subscriber_count * 0.1 
        return {
            "estimated_views": int(est_views),
            "estimated_cpv": 0.0, # calculated in frontend based on budget
            "confidence": "low (heuristic)"
        }
        
    model = joblib.load(MODEL_PATH)
    
    # Predict
    input_data = pd.DataFrame({
        "subscriber_count": [subscriber_count],
        "engagement_score": [engagement_score]
    })
    
    pred_views = model.predict(input_data)[0]
    
    return {
        "estimated_views": int(pred_views),
        "confidence": "high (ml_model)"
    }
