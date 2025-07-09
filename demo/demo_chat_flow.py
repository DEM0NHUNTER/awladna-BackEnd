# BackEnd/demo/demo_chat_flow.py
import asyncio
from datetime import datetime

# Import database session handler
from BackEnd.Utils.database import Session
# Import AI integration function to get AI-generated responses
from BackEnd.Utils.ai_integration import get_ai_response
# Import token creation and decoding utilities
from BackEnd.Utils.security import create_access_token, decode_token
# Import token store (if needed for token caching/validation)
from BackEnd.Utils.token_store import token_store
# Import ORM models
from BackEnd.Models.user import User
from BackEnd.Models.chat_log import ChatLog
from BackEnd.Models.child_profile import ChildProfile


async def demo_chat_flow():
    # Create a new database session
    db = Session()
    try:
        # 1) Query for a verified user in the database
        user = db.query(User).filter(User.is_verified.is_(True)).first()
        if not user:
            print("❌ No verified user found.")
            return

        # Query for a child profile associated with this user
        child = db.query(ChildProfile).filter(ChildProfile.user_id == user.user_id).first()
        if not child:
            print("❌ No child profile found. Run child demo first.")
            return

        print(f"\n👤 Using user {user.email!r}, chatting about {child.name}")

        # 2) Simulate issuing an access token for this user
        access_token = create_access_token({"sub": user.email})
        # Decode the access token to validate contents
        payload = decode_token(access_token)
        # Ensure the token payload subject matches the user's email
        assert payload.get("sub") == user.email

        # 3) Simulate sending a question to the AI assistant with child context
        user_input = "My child has a tantrum every evening before bed. What can I do?"
        ai_resp = await get_ai_response(
            user_input=user_input,
            child_age=child.age,
            child_name=child.name,
            context="bedtime_routine"  # Context for AI to tailor response
        )

        # Print AI-generated response and metadata
        print("\n🤖 AI Response:")
        print(ai_resp["response"])
        print("Suggested actions:", ai_resp["suggested_actions"])
        print("Sentiment:", ai_resp["sentiment"], ai_resp["sentiment_score"])

        # 4) Save the chat log to PostgreSQL database for record keeping
        log = ChatLog(
            user_id=user.user_id,
            child_id=child.child_id,
            user_input=user_input,
            chatbot_response=ai_resp["response"],
            sentiment_score=ai_resp["sentiment_score"],
            context="bedtime_routine"
        )
        db.add(log)   # Add the new log entry to the session
        db.commit()   # Commit transaction to persist the chat log

        print(f"\n✅ Chat stored (log id={log.id}) at {log.timestamp}")

    finally:
        # Always close the DB session to release connection resources
        db.close()


# If this script is run directly, run the async demo chat flow
if __name__ == "__main__":
    asyncio.run(demo_chat_flow())
