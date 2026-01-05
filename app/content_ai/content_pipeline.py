from app.content_ai.trends_fetcher import get_trending_topics as fetch_youtube_trends
from app.content_ai.content_analyzer import extract_topics
from app.content_ai.content_generator1 import generate_content_ideas
from app.db.mongo import db


def generate_campaign_content(campaign_id, influencer_id):
    brand_dna = db.brand_dna.find_one({"campaign_id": campaign_id})
    influencer_dna = db.influencer_dna.find_one({"influencer_id": influencer_id})

    if not brand_dna or not influencer_dna:
        raise Exception("Missing brand or influencer DNA")

    category = brand_dna.get("category", "")
    trends = fetch_youtube_trends(category)

    trend_titles = [t["title"] for t in trends]
    trend_topics = extract_topics(trend_titles)

    ideas = generate_content_ideas(
        brand_dna=brand_dna,
        influencer_dna=influencer_dna,
        trending_topics=trend_topics
    )

    return {
        "campaign_id": campaign_id,
        "influencer_id": influencer_id,
        "trending_topics": trend_topics[:10],
        "content_ideas": ideas
    }
