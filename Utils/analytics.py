# BackEnd/Utils/analytics.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from BackEnd.Models.chat_log import ChatLog
from BackEnd.Models.user import User
# from BackEnd.Schemas.analytics import FeedbackReportItem, FeedbackEffectivenessResponse
import logging

logger = logging.getLogger(__name__)


def get_feedback_summary(db: Session) -> Dict:
    """Get high-level feedback metrics"""
    total_feedback = db.query(func.count(ChatLog.id)).filter(ChatLog.rating.isnot(None)).scalar() or 0
    avg_rating = db.query(func.avg(ChatLog.rating)).filter(ChatLog.rating.isnot(None)).scalar() or 0

    return {
        "total_feedback": total_feedback,
        "average_rating": round(avg_rating, 2),
        "feedback_rate": round((total_feedback / db.query(func.count(ChatLog.id)).scalar()) * 100,
                               1) if total_feedback > 0 else 0
    }


def calculate_feedback_trend(db: Session, days: int = 30) -> Dict[str, List]:
    """Calculate feedback trends over time"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    feedback_logs = db.query(ChatLog).filter(
        ChatLog.rating.isnot(None),
        ChatLog.timestamp.between(start_date, end_date)
    ).order_by(ChatLog.timestamp).all()

    # Group by day
    daily_counts = {}
    for log in feedback_logs:
        date_key = log.timestamp.strftime("%Y-%m-%d")
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

    return {
        "dates": sorted(daily_counts.keys()),
        "counts": [daily_counts[date] for date in sorted(daily_counts.keys())]
    }


def get_sentiment_correlation(db: Session) -> Dict[str, float]:
    """Calculate correlation between sentiment and ratings"""
    logs = db.query(ChatLog).filter(
        ChatLog.rating.isnot(None),
        ChatLog.sentiment_score.isnot(None)
    ).all()

    if not logs:
        return {"correlation": 0.0}

    # Simple linear regression approximation
    sum_xy = sum(log.rating * log.sentiment_score for log in logs)
    sum_x = sum(log.rating for log in logs)
    sum_y = sum(log.sentiment_score for log in logs)
    sum_x2 = sum(log.rating ** 2 for log in logs)

    n = len(logs)
    try:
        correlation = (n * sum_xy - sum_x * sum_y) / (
            ((n * sum_x2 - sum_x ** 2) * (n * sum(sum_y ** 2)) ** 0.5
             ))
    except ZeroDivisionError:
        correlation = 0.0

    return {"correlation": round(correlation, 2)}


def get_child_feedback_stats(db: Session) -> List[Dict]:
    """Get feedback statistics per child"""
    results = db.query(
        ChatLog.child_id,
        func.count(ChatLog.id).filter(ChatLog.rating.isnot(None)).label("total_feedback"),
        func.avg(ChatLog.rating).label("avg_rating")
    ).group_by(ChatLog.child_id).all()

    return [
        {"child_id": str(child_id), "total_feedback": total, "avg_rating": round(avg, 2)}
        for child_id, total, avg in results
    ]


def analyze_recommendation_effectiveness(db: Session) -> Dict:
    """Analyze how feedback impacts recommendation effectiveness"""
    recent_feedback = db.query(ChatLog).filter(
        ChatLog.rating.isnot(None),
        ChatLog.timestamp > datetime.utcnow() - timedelta(days=90)
    ).all()

    # Calculate improvement rate (rating increase between consecutive interactions)
    improvement_count = 0
    for i in range(1, len(recent_feedback)):
        if recent_feedback[i].rating > recent_feedback[i - 1].rating:
            improvement_count += 1

    improvement_rate = round((improvement_count / len(recent_feedback)) * 100, 1) if recent_feedback else 0

    return {
        "improvement_rate": f"{improvement_rate}%",
        "feedback_volume": len(recent_feedback),
        "top_improvement_areas": ["bedtime_routine", "emotional_support", "behavior_management"][:3]
    }