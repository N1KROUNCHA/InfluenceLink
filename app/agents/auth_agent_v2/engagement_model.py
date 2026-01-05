from sklearn.ensemble import IsolationForest
import numpy as np

def train_engagement_model(feature_matrix):
    model = IsolationForest(
        n_estimators=100,
        contamination=0.15,
        random_state=42
    )
    model.fit(feature_matrix)
    return model

def engagement_anomaly_score(model, feature_vector):
    score = model.decision_function([feature_vector])[0]
    # normalize to 0–1
    return round((score + 0.5), 3)
