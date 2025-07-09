# BackEnd/Routes/chat.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging

from BackEnd.Models.chat_log import ChatLog
from BackEnd.Models.child_profile import ChildProfile
from BackEnd.Models.user import User
from BackEnd.Models.recommendation import Recommendation
from BackEnd.Schemas.chat import ChatRequest, ChatResponse
from BackEnd.Utils.database import get_db
from BackEnd.Utils.auth_utils import get_current_user
from BackEnd.Utils.ai_integration import get_ai_response
from BackEnd.Utils.mongo_client import chat_sessions_collection
from BackEnd.Utils.encryption import encrypt_data, decrypt_data
from BackEnd.Utils.recommendation_generator import generate_recommendations_from_emotion

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)


@router.get("/health")
def chat_health():
    return {"status": "Chat API is running"}


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = db.query(ChildProfile).filter(
        ChildProfile.child_id == chat_request.child_id,
        ChildProfile.user_id == current_user.user_id
    ).first()

    if not child:
        raise HTTPException(status_code=403, detail="Child profile not found or access denied")

    try:
        ai_payload = await get_ai_response(
            user_input=chat_request.message,
            child_age=child.age,
            child_name=child.name,
            context=chat_request.context,
        )
    except Exception as e:
        logger.error("AI integration failed", exc_info=True)
        raise HTTPException(status_code=502, detail="AI service unavailable")

    try:
        for rec in ai_payload.get("ai_recommendations", []):
            db.add(Recommendation(child_id=chat_request.child_id, **rec))
        db.commit()
    except Exception as rec_err:
        logger.warning("Failed to save AI recommendations: %s", rec_err)

    enc_input = encrypt_data(chat_request.message)
    enc_response = encrypt_data(ai_payload["response"])

    chat_log = ChatLog(
        user_id=current_user.user_id,
        child_id=chat_request.child_id,
        user_input=enc_input,
        chatbot_response=enc_response,
        context=chat_request.context,
        sentiment_score=ai_payload.get("sentiment_score", 0.0)
    )
    db.add(chat_log)
    db.commit()
    db.refresh(chat_log)

    try:
        chat_sessions_collection.insert_one({
            "user_id": current_user.user_id,
            "child_id": chat_request.child_id,
            "user_input": chat_request.message,
            "ai_response": ai_payload["response"],
            "context": chat_request.context,
            "sentiment": ai_payload.get("sentiment", "neutral"),
            "sentiment_score": ai_payload.get("sentiment_score", 0.0),
            "timestamp": datetime.utcnow()
        })
    except Exception as mongo_err:
        logger.warning("MongoDB log failed: %s", mongo_err)

    try:
        score = ai_payload.get("sentiment_score")
        if score is not None and score < -0.4:
            emotion_data = ai_payload.get("emotional_analysis", {})
            auto_recs = generate_recommendations_from_emotion(emotion_data)

            for rec in auto_recs:
                db.add(Recommendation(child_id=chat_request.child_id, **rec))
            db.commit()
    except Exception as rec_err:
        logger.warning("Failed to generate emotion-based recommendations: %s", rec_err)

    return ChatResponse(
        response=ai_payload["response"],
        suggested_actions=ai_payload.get("suggested_actions", []),
        sentiment=ai_payload.get("sentiment", "neutral"),
        timestamp=chat_log.timestamp
    )


@router.get("/history/{child_id}", response_model=List[ChatResponse])
def get_chat_history(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = (
        db.query(ChatLog)
        .filter(ChatLog.user_id == current_user.user_id, ChatLog.child_id == child_id)
        .order_by(ChatLog.timestamp.asc())
        .all()
    )

    return [
        ChatResponse(
            response=decrypt_data(log.chatbot_response),
            suggested_actions=[],
            sentiment="unknown",
            timestamp=log.timestamp,
        )
        for log in logs
    ]
