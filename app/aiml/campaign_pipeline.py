from app.aiml.build_campaign_training_data1 import build_campaign_training_data
from app.aiml.train_campaign_match_model1 import train_model
from app.aiml.predict_campaign_ranking1 import predict_campaign_ranking
from app.agents.brand_dna.brand_dna_builder import build_brand_dna



def run_campaign_pipeline(campaign_id: int):
    build_campaign_training_data(campaign_id)
    train_model()
    predict_campaign_ranking(campaign_id)
