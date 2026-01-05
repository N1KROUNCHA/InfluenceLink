from app.db.mongo import db

db.test.insert_one({
    "message": "InfluenceLink MongoDB working",
    "status": "success"
})

print("MongoDB write successful")
