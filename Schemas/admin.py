# BackEnd/Schemas/admin.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class FeedbackReportItem(BaseModel):
    """Schema for individual feedback records in reports"""
    chat_log_id: str
    user_id: str
    child_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
    timestamp: datetime


class FeedbackStatsResponse(BaseModel):
    """Schema for overall feedback statistics"""
    total_feedback: int
    average_rating: float
    feedback_rate: float  # Percentage of chats with feedback


class FeedbackTrendResponse(BaseModel):
    """Schema for feedback trend analysis"""
    dates: List[str]
    counts: List[int]


class SentimentCorrelationResponse(BaseModel):
    """Schema for sentiment-rating correlation"""
    correlation: float  # Pearson correlation coefficient


class ChildFeedbackStatsResponse(BaseModel):
    """Schema for child-specific feedback stats"""
    child_id: str
    total_feedback: int
    avg_rating: float


class RecommendationEffectivenessResponse(BaseModel):
    """Schema for recommendation effectiveness analysis"""
    improvement_rate: str  # e.g., "45%"
    feedback_volume: int
    top_improvement_areas: List[str]


class AdminUserOverview(BaseModel):
    """Schema for admin user management dashboard"""
    total_users: int
    active_users: int
    user_growth_rate: float  # Percentage change
    avg_feedback_per_user: float
    child_profiles: Dict[str, int]  # {child_id: feedback_count}


class AdminDashboardResponse(BaseModel):
    """Combined schema for admin dashboard"""
    feedback_stats: FeedbackStatsResponse
    feedback_trend: FeedbackTrendResponse
    child_stats: List[ChildFeedbackStatsResponse]
    recommendation_effectiveness: RecommendationEffectivenessResponse
    sentiment_correlation: SentimentCorrelationResponse
    user_overview: AdminUserOverview
