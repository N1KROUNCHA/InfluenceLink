from app.aiml.dataset_builder import load_dataset
from app.aiml.preprocess import normalize_features
from app.aiml.ranking_model import compute_ranking_score

df = load_dataset()
X = normalize_features(df)
scores = compute_ranking_score(X)

df["ranking_score"] = scores
df = df.sort_values(by="ranking_score", ascending=False)

print(df.head())
