from app.db.mongo import db
from app.db.mysql import cursor
from app.agents.auth_agent_v2.engagement_model import (
    train_engagement_model,
    engagement_anomaly_score
)
from app.agents.auth_agent_v2.comment_nlp_model import comment_quality_score
from app.agents.auth_agent_v2.temporal_model import temporal_consistency_score
from app.agents.auth_agent_v2.scorer import final_authenticity_score
import numpy as np

def run_auth_pipeline():
    influencers = list(db.influencer_dna.find())

    feature_matrix = []
    feature_map = {}

    for inf in influencers:
        cursor.execute("""
            SELECT subscriber_count, avg_views, engagement_score, video_count
            FROM influencers WHERE channel_id=%s
        """, (inf["channel_id"],))
        row = cursor.fetchone()
        if row:
            vec = list(row)
            feature_matrix.append(vec)
            feature_map[inf["channel_id"]] = vec

    model = train_engagement_model(feature_matrix)

    for inf in influencers:
        channel_id = inf["channel_id"]

        vec = feature_map.get(channel_id)
        if not vec:
            continue

        eng_score = engagement_anomaly_score(model, vec)

        comments = inf.get("recent_comments", [])
        comment_score = comment_quality_score(comments)

        views_series = inf.get("recent_views", [])
        temporal_score = temporal_consistency_score(views_series)

        final_score = final_authenticity_score(
            eng_score,
            comment_score,
            temporal_score
        )

        db.influencer_dna.update_one(
            {"channel_id": channel_id},
            {"$set": {"authenticity_score": final_score}}
        )

        print(f"✅ {channel_id} authenticity → {final_score}")

    print("\n🎉 AIML Authenticity Pipeline Complete")

if __name__ == "__main__":
    run_auth_pipeline()
