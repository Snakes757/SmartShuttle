import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. Load Environment Variables ---
# Determine the root path (two folders up from this script: app/scripts -> app -> root)
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
backend_root = os.path.dirname(app_dir)

# Load the .env file explicitly from the backend root
env_path = os.path.join(backend_root, '.env')
load_dotenv(dotenv_path=env_path)

# --- 2. Initialize Firebase DIRECTLY ---
# We initialize it here to avoid any circular imports from app.core.config
def init_firebase_for_script():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
        
        if cred_path and os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin initialized securely using credentials file.")
            except Exception as e:
                print(f"Failed to initialize Firebase Admin: {e}")
                sys.exit(1)
        else:
            print(f"FIREBASE_CREDENTIALS_PATH not found or invalid at: {cred_path}")
            print("Please ensure your .env file has a valid FIREBASE_CREDENTIALS_PATH.")
            # We exit here because seeding requires a valid DB connection
            sys.exit(1)


def seed_database():
    print("Initializing Firebase Admin SDK for Seeding...")
    init_firebase_for_script()
    db = firestore.client()

    print("Seeding Firestore with mock data for SmartShuttle...")

    # ---------------------------------------------------------
    # 1. Seed Routes
    # ---------------------------------------------------------
    route_1_id = str(uuid.uuid4())
    route_2_id = str(uuid.uuid4())
    
    routes = [
        {
            "id": route_1_id,
            "name": "Pretoria CBD to Johannesburg Park Station",
            "point_a_start": "Pretoria CBD",
            "point_b_end": "Johannesburg Park Station",
            "base_distance_km": 60.5
        },
        {
            "id": route_2_id,
            "name": "Centurion to Midrand Mall of Africa",
            "point_a_start": "Centurion Gautrain Station",
            "point_b_end": "Midrand Mall of Africa",
            "base_distance_km": 25.0
        }
    ]

    for r in routes:
        db.collection("routes").document(r["id"]).set(r)
    print(f"✅ Added {len(routes)} Routes.")

    # ---------------------------------------------------------
    # 2. Seed Passengers (Demonstrating <18 Parental Consent Rule)
    # ---------------------------------------------------------
    parent_id = str(uuid.uuid4())
    child_id = str(uuid.uuid4())
    
    passengers = [
        {
            "id": parent_id,
            "full_name": "Tau Senior",
            "gender": "Male",
            "id_number": "8501015000000",
            "age": 41,
            "email": "tau.parent@example.com",
            "phone_number": "0820000001",
            "parent_id": None,
            "is_verified": True
        },
        {
            "id": child_id,
            "full_name": "Tau Junior",
            "gender": "Male",
            "id_number": "1001015000000",
            "age": 16, # Under 18
            "email": "tau.student@example.com",
            "phone_number": "0820000002",
            "parent_id": parent_id, # Tied to the parent account
            "is_verified": True
        }
    ]

    for p in passengers:
        db.collection("passengers").document(p["id"]).set(p)
    print(f"✅ Added {len(passengers)} Passengers.")

    # ---------------------------------------------------------
    # 3. Seed Shuttle Owners (Demonstrating 7-seater rule)
    # ---------------------------------------------------------
    owner_1_id = str(uuid.uuid4())
    owner_2_id = str(uuid.uuid4())
    
    owners = [
        {
            "id": owner_1_id,
            "full_name": "James Shuttle",
            "email": "james.shuttle@example.com",
            "phone_number": "0730000001",
            "is_approved_by_admin": True,
            "vehicle": {
                "make_model": "Toyota Quantum",
                "capacity": 15,
                "has_trailer": False,
                "drivers_license_url": "https://example.com/license.jpg",
                "pdp_document_url": "https://example.com/pdp.jpg",
                "dekra_report_url": "https://example.com/dekra.jpg",
                "vehicle_photos_urls": ["https://example.com/van1.jpg"]
            }
        },
        {
            "id": owner_2_id,
            "full_name": "Lethabo Transport",
            "email": "lethabo.shuttle@example.com",
            "phone_number": "0730000002",
            "is_approved_by_admin": True,
            "vehicle": {
                "make_model": "Toyota Avanza",
                "capacity": 7,
                "has_trailer": True, # Required by your business rules for 7 seaters
                "drivers_license_url": "https://example.com/license2.jpg",
                "pdp_document_url": "https://example.com/pdp2.jpg",
                "dekra_report_url": "https://example.com/dekra2.jpg",
                "vehicle_photos_urls": ["https://example.com/van2.jpg"]
            }
        }
    ]

    for o in owners:
        db.collection("shuttle_owners").document(o["id"]).set(o)
    print(f"✅ Added {len(owners)} Shuttle Owners.")

    # ---------------------------------------------------------
    # 4. Seed Upcoming Trips
    # ---------------------------------------------------------
    trip_id = str(uuid.uuid4())
    # Schedule a trip for exactly 24 hours from now
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    
    trips = [
        {
            "id": trip_id,
            "route_id": route_1_id,
            "driver_id": owner_1_id,
            "departure_time": tomorrow.isoformat(),
            "status": "Pending"
        }
    ]

    for t in trips:
        db.collection("trips").document(t["id"]).set(t)
    print(f"✅ Added {len(trips)} Trips.")

    print("🎉 Database seeding successfully completed!")

if __name__ == "__main__":
    seed_database()