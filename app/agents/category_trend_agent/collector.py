from app.db.mongo import db

def collect_video_texts():
    videos = list(db.videos.find())

    docs = []
    for v in videos:
        text = f"{v.get('title','')} {v.get('description','')}".strip()
        if len(text.split()) > 10:
            docs.append({
                "channel_id": v["channel_id"],
                "text": text
            })
    return docs
