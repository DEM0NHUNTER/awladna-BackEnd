# BackEnd/demo/demo_sentiment_report.py
from BackEnd.Utils.database import Session
from BackEnd.Models.user import User
from BackEnd.Models.chat_log import ChatLog
from sqlalchemy import func


def demo_sentiment_report():
    """
    Demo function to generate a sentiment report for all children
    of a verified user by calculating average sentiment scores
    from chat logs.
    """
    db = Session()
    try:
        # Fetch a verified user from the database
        user = db.query(User).filter(User.is_verified.is_(True)).first()
        if not user:
            print("❌ No verified user.")
            return

        # Import ChildProfile model here to avoid circular import issues
        from BackEnd.Models.child_profile import ChildProfile

        # Fetch all child profiles associated with the user
        children = db.query(ChildProfile).filter(ChildProfile.user_id == user.user_id).all()

        # For each child, calculate the average sentiment score from their chat logs
        for child in children:
            avg_sent = (
                db.query(func.avg(ChatLog.sentiment_score))  # Calculate average sentiment_score
                .filter(ChatLog.child_id == child.child_id)  # Filter logs for the current child
                .scalar()  # Get scalar value of average
            ) or 0  # Default to 0 if no logs found

            # Print the child's name and their average sentiment score formatted to 2 decimals
            print(f"{child.name}: avg sentiment = {avg_sent:.2f}")
    finally:
        # Always close the database session to free resources
        db.close()


if __name__ == "__main__":
    demo_sentiment_report()
