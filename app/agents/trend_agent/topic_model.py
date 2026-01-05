from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_trending_topics(texts, k=5):
    # 🔒 SAFETY CHECK
    if not texts or len(texts) < 3:
        print("⚠️ Not enough text data for topic modeling")
        return []

    embeddings = model.encode(texts)

    if len(embeddings) < k:
        k = max(1, len(embeddings) // 2)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    cluster_strength = np.bincount(labels) / len(labels)
    return cluster_strength.tolist()
