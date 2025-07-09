# BackEnd/Schemas/analytics.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


# Feedback Types
class FeedbackType(str, Enum):
    """Type of feedback based on context"""
    BEHAVIORAL = "behavioral"
    EMOTIONAL = "emotional"
    COMMUNICATION = "communication"
    OTHER = "other"


# Base Feedback Schema
class FeedbackItem(BaseModel):
    """Schema for individual feedback records"""
    chat_log_id: str
    user_id: str
    child_id: str
    rating: int = Field(..., ge=1, le=5)  # Rating 1–5
    feedback: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)  # -1 to 1
    timestamp: datetime


# Aggregated Feedback Stats
class FeedbackSummary(BaseModel):
    """High-level feedback statistics"""
    total_feedback: int
    average_rating: float
    feedback_rate: float  # Percentage of chats with feedback
    last_updated: datetime


# Trend Analysis
class FeedbackTrendItem(BaseModel):
    date: str  # Format: "YYYY-MM-DD"
    count: int
    average_rating: float


class FeedbackTrendResponse(BaseModel):
    """Schema for feedback trends over time"""
    period: str  # e.g., "30_days", "90_days"
    trends: List[FeedbackTrendItem]
    overall_change: float  # % change from previous period


# Child-Specific Feedback
class ChildFeedbackStats(BaseModel):
    """Schema for child-specific feedback metrics"""
    child_id: str
    total_feedback: int
    avg_rating: float
    improvement_rate: float  # % improvement between sessions
    last_feedback_date: Optional[datetime] = None


# Recommendation Effectiveness
class RecommendationEffectiveness(BaseModel):
    """Schema for recommendation impact analysis"""
    recommendation_type: str
    feedback_volume: int
    avg_rating: float
    improvement_rate: float  # % of users reporting improvement
    top_improvement_areas: List[str]


# Sentiment Correlation
class SentimentRatingCorrelation(BaseModel):
    """Schema for sentiment-rating analysis"""
    sentiment_category: str  # e.g., "positive", "neutral", "negative"
    avg_rating: float
    feedback_count: int
    improvement_rate: float


# Admin Dashboard Overview
class AdminDashboardStats(BaseModel):
    """Combined schema for admin analytics dashboard"""
    feedback_summary: FeedbackSummary
    feedback_trend: FeedbackTrendResponse
    child_stats: List[ChildFeedbackStats]
    recommendation_effectiveness: List[RecommendationEffectiveness]
    sentiment_correlation: List[SentimentRatingCorrelation]
    system_health: Dict[str, str]  # System status metrics


# Exportable Report Schema
class FeedbackReportItem(BaseModel):
    """Schema for exportable feedback records"""
    chat_log_id: str
    user_email: str
    child_name: str
    rating: int
    feedback: Optional[str] = None
    sentiment_score: float
    context_tags: List[str]
    timestamp: datetime


class FeedbackReportResponse(BaseModel):
    """Schema for full feedback reports"""
    report_id: str
    generated_at: datetime
    time_range: str  # e.g., "2025-01-01_to_2025-06-27"
    total_records: int
    feedback_items: List[FeedbackReportItem]
    summary: Dict[str, float]  # Average ratings, growth metrics
