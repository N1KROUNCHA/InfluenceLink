import random
from app.content_ai.trend_provider import CATEGORY_TRENDS, HOOK_TEMPLATES
from app.content_ai.script_generator import generate_script

def generate_content_ideas(brand, influencers):
    category = brand.get("category", "general")
    style = brand.get("required_style", "neutral")

    trends = CATEGORY_TRENDS.get(category, [])
    if not trends:
        trends = CATEGORY_TRENDS["technology"]

    influencer_topics = []
    influencer_styles = []

    for inf in influencers:
        influencer_topics.extend(inf.get("topics", []))
        influencer_styles.append(inf.get("style", "neutral"))

    influencer_topics = list(set(influencer_topics))[:5]
    influencer_style = max(set(influencer_styles), key=influencer_styles.count)

    ideas = []

    for topic in random.sample(trends, min(3, len(trends))):
        ideas.append({
            "title": f"{topic} – Explained Simply",
            "hook": random.choice(HOOK_TEMPLATES),
            "format": "YouTube Short",
            "tone": influencer_style or style,
            "script": generate_script(topic, style),
            "caption": f"{topic} 🚀 #shorts #{category}",
            "cta": "Follow for more insights",
            "why_it_works": "Matches YouTube short-form trend + influencer style"
        })

    return ideas
