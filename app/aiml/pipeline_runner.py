from app.aiml.run_campaign_matching import run_campaign_matching
from app.aiml.predict_campaign_ranking import predict_campaign_ranking

def run_full_campaign_pipeline(campaign_id: int):
    # Step 1: DNA similarity
    run_campaign_matching(campaign_id)

    # Step 2: ML ranking prediction
    predict_campaign_ranking(campaign_id)
