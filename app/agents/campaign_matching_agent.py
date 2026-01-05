from app.aiml.campaign_match_model import predict_match_score
from app.aiml.siamese_infer import compute_similarity
from app.db.mysql import fetch_campaign, fetch_influencers

def run_campaign_matching(campaign_id):
    campaign = fetch_campaign(campaign_id)
    influencers = fetch_influencers(campaign)

    results = []

    for inf in influencers:
        semantic_score = compute_similarity(
            campaign["embedding"],
            inf["dna_embedding"]
        )

        ml_score = predict_match_score(
            campaign, inf, semantic_score
        )

        final_score = 0.7 * ml_score + 0.3 * semantic_score

        results.append({
            "influencer_id": inf["id"],
            "score": final_score
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:5]
