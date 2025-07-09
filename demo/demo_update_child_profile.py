# BackEnd/demo/demo_update_child_profile.py
import json
from BackEnd.Utils.database import Session
from BackEnd.Models.user import User
from BackEnd.Models.child_profile import ChildProfile
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


def demo_update_child_profile():
    """
    Demo function to update behavioral and emotional settings
    of a verified user's child profile.
    """
    db = Session()
    try:
        # Fetch the first verified user from the database
        user = db.query(User).filter(User.is_verified.is_(True)).first()
        if not user:
            print("❌ No verified user.")
            return

        # Fetch the first child profile linked to the user
        child = db.query(ChildProfile).filter(ChildProfile.user_id == user.user_id).first()
        if not child:
            print("❌ No child profile.")
            return

        # Display current behavioral and emotional data (decrypted)
        print(f"\n✏️  Current settings for {child.name}:")
        print("Behavioral:", child.get_behavioral_data())
        print("Emotional:", child.get_emotional_data())

        # Define new behavioral and emotional data to update
        new_behavior = {"attention_span": "medium", "temperament": "calm"}
        new_emotion = {"emotional_needs": "routine", "anxieties": []}

        # Update the child profile's sensitive data (will be encrypted internally)
        child.set_behavioral_data(new_behavior)
        child.set_emotional_data(new_emotion)

        # Commit the changes to the database
        db.commit()
        db.refresh(child)  # Refresh the instance with updated data

        # Display updated behavioral and emotional data
        print(f"\n✅ Updated settings for {child.name}:")
        print("Behavioral:", child.get_behavioral_data())
        print("Emotional:", child.get_emotional_data())

    finally:
        # Close the DB session to release resources
        db.close()


if __name__ == "__main__":
    demo_update_child_profile()

