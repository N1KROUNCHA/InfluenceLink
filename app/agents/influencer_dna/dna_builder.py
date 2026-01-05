from sentence_transformers import SentenceTransformer
from app.db.mongo import db
from app.agents.influencer_dna.nlp_agent import extract_nlp_profile
from app.agents.influencer_dna.vision_agent import extract_dominant_colors

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def build_influencer_dna(channel_doc, influencer_id):
    snippet = channel_doc.get("snippet", {})

    title = snippet.get("title", "")
    description = snippet.get("description", "")
    thumbnail = snippet.get("thumbnails", {}).get("high", {}).get("url", "")

    text = f"{title} {description}".strip()

    nlp_data = extract_nlp_profile(text)
    embedding = model.encode(text).tolist() if text else []

    colors = extract_dominant_colors(thumbnail)

    dna = {
        "influencer_id": influencer_id,

        # NLP
        "embedding": embedding,
        "topics": nlp_data["topics"],
        "entities": nlp_data["entities"],
        "sentiment": nlp_data["sentiment"],
        "language": nlp_data["language"],
        "region": nlp_data["region"],
        "style": nlp_data["style"],
        "authenticity_score": nlp_data["authenticity"],

        # Vision
        "color_palette": colors,

        "updated_at": None
    }

    db.influencer_dna.update_one(
        {"influencer_id": influencer_id},
        {"$set": dna},
        upsert=True
    )

    return dna
