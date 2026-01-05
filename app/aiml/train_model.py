from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from app.aiml.dataset_builder import load_dataset
import joblib

def train():
    X, y = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)

    print("Model trained successfully")
    print("Mean Absolute Error:", round(mae, 4))

    joblib.dump(model, "app/aiml/influencer_model.pkl")

if __name__ == "__main__":
    train()
