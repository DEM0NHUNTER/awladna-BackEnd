"""
Demo Flow:
1. Load verified user from DB
2. Create a new Child Profile with personalization
3. Store to PostgreSQL
4. Sync to MongoDB for quick access
5. Print summary
"""

import random
from datetime import datetime

# Import User and ChildProfile ORM models
from BackEnd.Models.user import User
from BackEnd.Models.child_profile import ChildProfile

# Import database session and MongoDB collection helper
from BackEnd.Utils.database import Session, get_mongo_collection_custom


def demo_child_profile_flow(mongo_url=None):
    # Create a new database session (PostgreSQL)
    db = Session()
    try:
        # Step 1: Query for the first verified user from the relational database
        user = db.query(User).filter(User.is_verified.is_(True)).first()
        if not user:
            print("❌ No verified users found. Please run authentication flow first.")
            return

        print(f"\n✅ Using user: {user.email}")

        # Step 2: Create a new ChildProfile instance associated with the user
        child_name = f"Child{random.randint(100, 999)}"  # Randomized name for demo
        child = ChildProfile(
            user_id=user.user_id,
            name=child_name,
            birth_date=datetime(2018, 6, 15),
            gender="male"
        )

        # Encrypt and set sensitive behavioral data
        child.set_behavioral_data({"attention_span": "short", "temperament": "high-energy"})
        # Encrypt and set sensitive emotional data
        child.set_emotional_data({"emotional_needs": "encouragement", "anxieties": ["separation"]})

        # Add the new child profile to the database session
        db.add(child)
        # Commit transaction to persist to PostgreSQL
        db.commit()
        # Refresh instance with DB-generated fields (e.g., child_id)
        db.refresh(child)

        print(f"\n✅ Created child profile: {child.name} (Age: {child.age})")

        # Step 3: Prepare document for MongoDB synchronization
        mongo_doc = {
            "child_id": child.child_id,
            "user_id": child.user_id,
            "name": child.name,
            "birth_date": child.birth_date.isoformat(),  # Store ISO string for compatibility
            "gender": child.gender,
            # Decrypt and include behavioral data for quick access in MongoDB
            "behavioral": child.get_behavioral_data(),
            # Decrypt and include emotional data
            "emotional": child.get_emotional_data(),
            "created_at": child.created_at.isoformat()
        }

        # Get MongoDB collection handle, optionally using a custom URL
        col = get_mongo_collection_custom("child_profiles", mongo_url)
        # Insert the child profile document into MongoDB
        col.insert_one(mongo_doc)
        print("✅ Synced to MongoDB")

        # Step 4: Print a summary of the created child profile
        print("\n--- Child Profile Summary ---")
        print(f"Name       : {child.name}")
        print(f"Gender     : {child.gender}")
        print(f"Behavior   : {child.get_behavioral_data()}")
        print(f"Emotions   : {child.get_emotional_data()}")

    finally:
        # Always close the DB session to free resources
        db.close()


# Run the demo flow if executed directly
if __name__ == "__main__":
    demo_child_profile_flow()
