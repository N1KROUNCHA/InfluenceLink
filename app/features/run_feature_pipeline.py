from app.db.mongo import db
from app.features.feature_extractor import extract_raw_features
from app.features.feature_builder import build_features


def run_pipeline():
    db.features.delete_many({})  # clean old features

    for channel in db.influencers_full.find():
        raw_features = extract_raw_features(channel)
        final_features = build_features(raw_features)

        db.features.insert_one({
            "channel_id": raw_features["channel_id"],
            "features": final_features
        })

        print("Features built for:", channel["snippet"]["title"])


if __name__ == "__main__":
    run_pipeline()
