from app.agents.trend_agent.trend_collector import collect_trend_documents
from app.agents.trend_agent.time_series_model import growth_score
from app.agents.trend_agent.topic_model import extract_trending_topics
from app.agents.trend_agent.scorer import trend_score
from app.db.mongo import db
import datetime

def run_trend_pipeline():
    docs = collect_trend_documents()

    if not docs:
        print("❌ No video documents found for trend analysis")
        return

    texts = [d["text"] for d in docs]

    if len(texts) < 3:
        print("❌ Not enough textual data to detect trends")
        return

    topic_strengths = extract_trending_topics(texts)

    if not topic_strengths:
        print("⚠️ Topic model skipped due to insufficient data")
        return

    trend_results = []
    for i, strength in enumerate(topic_strengths):
        score = trend_score(
            time_score=0.7,
            topic_score=strength,
            activity_score=0.6
        )

        trend_results.append({
            "cluster_id": i,
            "trend_score": score
        })

    db.trending_topics.delete_many({})
    db.trending_topics.insert_many(trend_results)

    print("🔥 Trend forecasting completed successfully")

if __name__ == "__main__":
    run_trend_pipeline()
