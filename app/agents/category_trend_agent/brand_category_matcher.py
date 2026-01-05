from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def match_brand_to_category(brand_category_text, category_embeddings):
    brand_emb = model.encode(brand_category_text)

    best_cat = None
    best_score = -1

    for cat, emb in category_embeddings.items():
        score = cosine(brand_emb, emb)
        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat, round(best_score, 3)
