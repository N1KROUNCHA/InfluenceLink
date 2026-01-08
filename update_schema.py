from app.db.mysql import conn, cursor

def update_schema():
    print("🔧 Updating Database Schema for Auth...")
    
    # 1. Update Brands Table
    try:
        cursor.execute("ALTER TABLE brands ADD COLUMN email VARCHAR(255) UNIQUE")
        print("✅ Added email to brands")
    except Exception as e:
        print(f"ℹ️ Brands email: {e}")

    try:
        cursor.execute("ALTER TABLE brands ADD COLUMN password_hash VARCHAR(255)")
        print("✅ Added password_hash to brands")
    except Exception as e:
        print(f"ℹ️ Brands password_hash: {e}")

    # 2. Update Influencers Table
    try:
        cursor.execute("ALTER TABLE influencers ADD COLUMN email VARCHAR(255) UNIQUE")
        print("✅ Added email to influencers")
    except Exception as e:
        print(f"ℹ️ Influencers email: {e}")

    try:
        cursor.execute("ALTER TABLE influencers ADD COLUMN password_hash VARCHAR(255)")
        print("✅ Added password_hash to influencers")
    except Exception as e:
        print(f"ℹ️ Influencers password_hash: {e}")

    conn.commit()
    print("🎉 Schema Update Complete")

if __name__ == "__main__":
    update_schema()
