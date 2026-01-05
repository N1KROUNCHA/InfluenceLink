from sentence_transformers import SentenceTransformer
import spacy

model = SentenceTransformer("all-MiniLM-L6-v2")
nlp = spacy.load("en_core_web_sm")


def extract_topics(texts):
    joined = " ".join(texts)
    doc = nlp(joined)

    topics = list(set([
        chunk.text.lower()
        for chunk in doc.noun_chunks
        if len(chunk.text) > 3
    ]))

    return topics[:15]


def embed_text(text):
    return model.encode(text).tolist()
