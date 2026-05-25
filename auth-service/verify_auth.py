
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to sys.path to allow imports from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.infrastructure.database import Base, get_db

# Use in-memory SQLite for verification
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def run_verification():
    print("--- Starting Auth Service Verification ---")
    
    # 1. Health Check
    print("\n1. Testing /health...")
    resp = client.get("/health")
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200

    # 2. Register a User
    print("\n2. Testing /auth/register (User)...")
    user_data = {
        "username": "testuser_verif",
        "email": "test_verif@example.com",
        "password": "password123",
        "role": "user"
    }
    resp = client.post("/auth/register", json=user_data)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 201

    # 3. Register an Admin
    print("\n3. Testing /auth/register (Admin)...")
    admin_data = {
        "username": "adminuser_verif",
        "email": "admin_verif@bookflow.com",
        "password": "adminpass123",
        "role": "admin"
    }
    resp = client.post("/auth/register", json=admin_data)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 201

    # 4. Login
    print("\n4. Testing /auth/login...")
    login_data = {"username": "testuser_verif", "password": "password123"}
    resp = client.post("/auth/login", data=login_data)
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    refresh_token = resp.json()["refresh_token"]
    print(f"Token Received (short): {token[:20]}...")
    print(f"Refresh Token Received (short): {refresh_token[:20]}...")

    # 5. Verify Token
    print("\n5. Testing /auth/verify...")
    resp = client.get("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["role"] == "user"

    # 6. Test Mock Token
    print("\n6. Testing /auth/mock-token...")
    resp = client.get("/auth/mock-token")
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200
    mock_token = resp.json()["access_token"]
    
    # 7. Verify Mock Token
    print("\n7. Verifying Mock Token...")
    resp = client.get("/auth/verify", headers={"Authorization": f"Bearer {mock_token}"})
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"

    # 8. Refresh Token
    print("\n8. Testing /auth/refresh...")
    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200
    new_token = resp.json()["access_token"]
    print(f"New Access Token Received (short): {new_token[:20]}...")

    # 9. Verify New Token
    print("\n9. Verifying New Access Token...")
    resp = client.get("/auth/verify", headers={"Authorization": f"Bearer {new_token}"})
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200

    # 10. Logout (Revoke)
    print("\n10. Testing /auth/logout...")
    resp = client.post("/auth/logout", headers={"Authorization": f"Bearer {new_token}"})
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200

    # 11. Verify Revoked Token
    print("\n11. Verifying Revoked Token (Should Fail)...")
    resp = client.get("/auth/verify", headers={"Authorization": f"Bearer {new_token}"})
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 401

    print("\n--- Verification Completed Successfully! ---")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if os.path.exists("./test.db"):
            os.remove("./test.db")
