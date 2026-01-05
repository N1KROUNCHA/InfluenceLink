import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.mysql import cursor, conn
from app.db.mongo import db
from app.agents.brand_safety_agent import BrandSafetyAgent

def backfill_brand_safety_scores():
    """
    Analyzes the content of all influencers and updates their brand safety scores.
    """
    agent = BrandSafetyAgent()
    
    # Get all influencers from the database
    cursor.execute("SELECT influencer_id FROM influencers")
    influencers = cursor.fetchall()

    if not influencers:
        print("No influencers found in the database.")
        return

    print(f"Found {len(influencers)} influencers to analyze...")

    for influencer_row in influencers:
        influencer_id = influencer_row['influencer_id']
        
        # Find all video content for the influencer from MongoDB
        videos = list(db.influencer_videos.find({"influencer_id": influencer_id}))
        
        if not videos:
            # If no videos, we can't score them, so we skip
            print(f"No videos found for influencer {influencer_id}, skipping.")
            continue

        total_score = 0
        analyzed_videos = 0
        
        for video in videos:
            # Analyze both the title and description
            title = video.get("title", "")
            description = video.get("description", "")
            
            # Combine them for a more comprehensive analysis
            content_to_analyze = f"{title}. {description}"
            
            if content_to_analyze.strip() == ".":
                continue

            analysis_result = agent.analyze_text(content_to_analyze)
            total_score += analysis_result["brand_safety_score"]
            analyzed_videos += 1

        if analyzed_videos > 0:
            # Calculate the average score across all their content
            average_score = total_score / analyzed_videos
            
            # Update the influencer's record in the database
            cursor.execute(
                "UPDATE influencers SET brand_safety_score = %s WHERE influencer_id = %s",
                (average_score, influencer_id)
            )
            print(f"Updated influencer {influencer_id} with brand safety score: {average_score:.2f}")
        else:
            print(f"No content to analyze for influencer {influencer_id}.")

    conn.commit()
    print("\n✅ Brand safety score backfill complete!")

if __name__ == "__main__":
    backfill_brand_safety_scores()

