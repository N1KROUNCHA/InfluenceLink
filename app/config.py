from dotenv import load_dotenv
import os

load_dotenv()

# Expose variables for import
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Debug prints (optional, can remove later)
print("YouTube Key Loaded:", bool(YOUTUBE_API_KEY))
print("Mongo URI Loaded:", bool(MONGO_URI))
print("MySQL Host:", MYSQL_HOST)
print("MySQL Port:", MYSQL_PORT)
