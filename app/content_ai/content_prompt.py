def build_prompt(brand, trends, influencers):
    return f"""
You are a social media strategist.

Brand info:
- Name: {brand.get("title")}
- Category: {brand.get("category")}
- Style: {brand.get("required_style")}
- Region: {brand.get("target_region")}

Trending topics:
{", ".join(trends)}

Influencer styles:
{", ".join([i.get("style","neutral") for i in influencers])}

Task:
Generate 5 high-performing content ideas.

Each idea must include:
1. Hook
2. Video script (short-form)
3. Caption
4. CTA
5. Why it works

Return clean JSON only.
"""
