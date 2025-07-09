# BackEnd/demo/demo_fetch_history.py
# Import database session utility and ORM models
from BackEnd.Utils.database import Session
from BackEnd.Models.user import User
from BackEnd.Models.chat_log import ChatLog
from BackEnd.Models.child_profile import ChildProfile


def demo_fetch_history(limit=5):
    """
    Fetches and prints the last `limit` chat messages for the first verified user’s child profile.
    Prints both the parent's input and AI responses along with sentiment scores.
    """
    db = Session()  # Create a new DB session
    try:
        # Find a verified user (assumes at least one exists)
        user = db.query(User).filter(User.is_verified.is_(True)).first()
        if not user:
            print("❌ No verified user.")
            return

        # Find a child profile linked to this user
        child = db.query(ChildProfile).filter(ChildProfile.user_id == user.user_id).first()
        if not child:
            print("❌ No child profile.")
            return

        print(f"\n📜 Fetching last {limit} messages for {child.name}:")

        # Query the ChatLog table for recent chat entries linked to the child,
        # ordered by timestamp descending, limited by `limit`
        history = (
            db.query(ChatLog)
            .filter(ChatLog.child_id == child.child_id)
            .order_by(ChatLog.timestamp.desc())
            .limit(limit)
            .all()
        )

        # Iterate through the results in chronological order (oldest first)
        for log in reversed(history):
            # Print timestamp, parent input message, AI response, and sentiment info
            print(f"\n[{log.timestamp:%Y-%m-%d %H:%M}] Parent: {log.user_input}")
            print(f"AI: {log.chatbot_response}")
            print(f"  Sentiment: {log.sentiment_score} ({log.get_sentiment_label()})")

    finally:
        # Close the DB session cleanly
        db.close()


# Run the fetch history demo if script is executed directly
if __name__ == "__main__":
    demo_fetch_history()
