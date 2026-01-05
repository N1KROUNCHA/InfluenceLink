from app.db.mongo import db

doc = {
    "test": "DNA_WRITE_TEST",
    "value": 123
}

db.influencer_dna.insert_one(doc)

print("Inserted test document")
