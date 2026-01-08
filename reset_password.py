from app.db.mysql import cursor
from passlib.context import CryptContext

def check_test_user():
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    # Check test_brand
    email = "test_brand@example.com"
    cursor.execute("SELECT brand_id, email, password_hash FROM brands WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if user:
        print(f"Test User found: {user['email']}")
        verify = pwd_context.verify("password123", user["password_hash"])
        print(f"Verify 'password123' for test user: {verify}")
    else:
        print("Test user not found")

    # Reset real user password
    real_email = "srinidhikrouncha1956@gmail.com"
    new_hash = pwd_context.hash("password123")
    
    cursor.execute("UPDATE brands SET password_hash = %s WHERE email = %s", (new_hash, real_email))
    from app.db.mysql import conn
    conn.commit()
    print(f"Reset password for {real_email} to 'password123'")

if __name__ == "__main__":
    check_test_user()
