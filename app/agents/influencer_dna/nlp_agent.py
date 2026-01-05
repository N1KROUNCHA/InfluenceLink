from langdetect import detect
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()


def extract_nlp_profile(text: str):
    if not text:
        return {
            "sentiment": 0.0,
            "topics": [],
            "entities": [],
            "language": "unknown",
            "region": "unknown",
            "style": "neutral",
            "authenticity": 0.5
        }

    try:
        language = detect(text)
    except:
        language = "unknown"

    doc = nlp(text)

    topics = list(set(chunk.text.lower() for chunk in doc.noun_chunks))[:10]
    entities = list(set(ent.label_ for ent in doc.ents))

    sentiment = sia.polarity_scores(text)["compound"]

    style = "motivational" if any(
        k in text.lower()
        for k in ["motivation", "fitness", "inspire", "hustle"]
    ) else "neutral"

    region = "india" if "india" in text.lower() else "unknown"

    authenticity = min(1.0, max(0.3, 0.5 + sentiment / 2))

    return {
        "sentiment": sentiment,
        "topics": topics,
        "entities": entities,
        "language": language,
        "region": region,
        "style": style,
        "authenticity": authenticity
    }
