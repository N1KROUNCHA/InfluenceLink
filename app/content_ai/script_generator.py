import random

def generate_script(topic, brand_style):
    return f"""
HOOK (0–3s):
{random.choice([
    "Most people get this wrong.",
    "Nobody explains this properly.",
    "Stop scrolling if you care about this."
])}

PROBLEM (3–10s):
People struggle with {topic.lower()} because they follow outdated advice.

VALUE (10–25s):
Here’s what actually works:
• Focus on the core mechanic
• Avoid beginner mistakes
• Use practical shortcuts

CTA (25–30s):
Follow for more real insights.
""".strip()
