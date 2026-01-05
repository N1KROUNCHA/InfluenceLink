from app.db.mysql import cursor
from app.agents.brand_dna.brand_dna_builder import build_brand_dna

def run_brand_dna(campaign_id):
    cursor.execute("""
        SELECT campaign_id, title, description, campaign_type, target_region
        FROM campaigns
        WHERE campaign_id = %s
    """, (campaign_id,))
    
    row = cursor.fetchone()
    if not row:
        print("❌ Campaign not found")
        return

    campaign = {
        "campaign_id": row[0],
        "title": row[1],
        "description": row[2],
        "campaign_type": row[3],
        "target_region": row[4]
    }

    build_brand_dna(campaign)

if __name__ == "__main__":
    run_brand_dna(2)   # ← use your campaign_id
