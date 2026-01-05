import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

def train_campaign_match_model(df):
    X = df.drop(columns=["performance_score"])
    y = df["performance_score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("MSE:", mean_squared_error(y_test, preds))

    joblib.dump(model, "models/campaign_match_model.pkl")
