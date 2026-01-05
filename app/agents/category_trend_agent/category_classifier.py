from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def classify_categories(docs, k=6):
    """
    Unsupervised category discovery using NLP embeddings
    """
    texts = [d["text"] for d in docs if d.get("text")]

    if len(texts) < 3:
        return {}

    embeddings = model.encode(texts)

    if len(embeddings) < k:
        k = max(1, len(embeddings) // 2)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    categorized = {}
    for i, label in enumerate(labels):
        categorized.setdefault(label, [])
        categorized[label].append(texts[i])

    return categorized


def category_embeddings(categorized):
    """
    Compute one embedding per discovered category
    """
    vectors = {}

    for cat, texts in categorized.items():
        emb = model.encode(texts)
        vectors[cat] = np.mean(emb, axis=0).tolist()

    return vectors
