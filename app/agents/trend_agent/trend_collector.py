from app.db.mongo import db

def collect_trend_documents():
    videos = list(db.videos.find())

    if not videos:
        return []

    influencer_text = {}

    for v in videos:
        channel_id = v.get("channel_id")
        title = v.get("title", "")
        desc = v.get("description", "")

        text = f"{title} {desc}".strip()
        if not text:
            continue

        influencer_text.setdefault(channel_id, "")
        influencer_text[channel_id] += " " + text

    docs = []
    for cid, text in influencer_text.items():
        if len(text.split()) > 20:   # minimum signal
            docs.append({
                "channel_id": cid,
                "text": text
            })

    return docs
