from app.agents.category_trend_agent.collector import collect_video_texts
from app.agents.category_trend_agent.category_classifier import (
    classify_categories,
    category_embeddings
)
from app.agents.category_trend_agent.trend_detector import detect_trends
from app.agents.category_trend_agent.content_suggester import suggest_content
from app.agents.category_trend_agent.brand_category_matcher import (
    match_brand_to_category
)
from app.db.mongo import db
import datetime


def run_category_trends(brand_category_text=None):
    """
    Runs category-agnostic trend detection and content suggestion.
    If brand_category_text is provided, matches brand to best trending category.
    """

    print("🔍 Collecting video text data...")
    docs = collect_video_texts()

    if not docs or len(docs) < 3:
        print("❌ Not enough video data to detect category-wise trends")
        return

    print(f"✅ Collected {len(docs)} video documents")

    print("🧠 Performing unsupervised category classification...")
    categorized = classify_categories(docs, k=6)

    if not categorized:
        print("❌ Category classification failed")
        return

    print(f"✅ Discovered {len(categorized)} dynamic categories")

    print("🧬 Computing category embeddings...")
    cat_vectors = category_embeddings(categorized)

    db.category_trends.delete_many({})

    category_results = {}

    print("🔥 Detecting trends per category...")
    for cat_id, texts in categorized.items():
        if len(texts) < 2:
            continue

        trends = detect_trends(texts)

        if not trends:
            continue

        content = suggest_content(f"Category-{cat_id}", trends)

        doc = {
            "category_id": f"Category-{cat_id}",
            "top_trends": trends,
            "content_ideas": content["suggestions"],
            "created_at": datetime.datetime.utcnow()
        }

        db.category_trends.insert_one(doc)
        category_results[cat_id] = doc

        print(f"✅ Trends stored for Category-{cat_id}")

    if not category_results:
        print("⚠️ No valid trends generated")
        return

    # OPTIONAL: Brand → Category Matching
    if brand_category_text:
        print("\n🎯 Matching brand category to trending categories...")
        best_cat, confidence = match_brand_to_category(
            brand_category_text,
            cat_vectors
        )

        print(
            f"🏆 Brand category '{brand_category_text}' "
            f"matched with Category-{best_cat} "
            f"(confidence={confidence})"
        )

        matched_trends = category_results.get(best_cat)

        if matched_trends:
            print("\n📌 Suggested Viral Content Ideas:")
            for idea in matched_trends["content_ideas"]:
                print(f"• {idea['idea']} ({idea['format']})")

    print("\n🎉 Category-wise Trend Intelligence Pipeline Completed")


if __name__ == "__main__":
    # Example brand input (can be changed dynamically later)
    run_category_trends(
        brand_category_text="fitness and health supplements"
    )
