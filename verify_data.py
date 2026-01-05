from app.db.mysql import conn, cursor
import os
from dotenv import load_dotenv

load_dotenv()

def verify():
    with open("verification.log", "w") as f:
        f.write("--- Style Verification ---\n")
        
        # Get distinct styles
        cursor.execute("SELECT DISTINCT style FROM influencers WHERE style IS NOT NULL")
        styles = cursor.fetchall()
        
        f.write(f"Found {len(styles)} unique styles:\n")
        for s in styles:
            style_name = s['style']
            if style_name:
                 f.write(f"- {style_name}\n")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"Error: {e}")
