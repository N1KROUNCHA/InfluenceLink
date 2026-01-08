from app.db.mysql import conn, cursor

def fix():
    print("🔧 Adding description column to influencers...")
    try:
        cursor.execute("ALTER TABLE influencers ADD COLUMN description TEXT")
        conn.commit()
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix()
