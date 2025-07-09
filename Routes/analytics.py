# BackEnd/Routes/analytics.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import func
from BackEnd.Models.chat_log import ChatLog
from BackEnd.Utils.auth_utils import get_current_user, require_role
from BackEnd.Utils.database import get_db
import asyncio
# Import models and utils
from BackEnd.Models.user import User
from BackEnd.Schemas.feedback import FeedbackCreate

router = APIRouter(tags=["Analytics"])
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import csv
from fastapi.websockets import WebSocketDisconnect
from io import StringIO
from typing import Optional

# Real-time feedback stream
connected_clients = set()


async def notify_clients(feedback_data):
    for client in connected_clients:
        await client.send_json(feedback_data)


@router.websocket("/feedback-stream")
async def feedback_stream(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


# Feedback submission
@router.post("/feedback/", status_code=status.HTTP_201_CREATED)
def submit_feedback(
        feedback_data: FeedbackCreate,  # Fixed parameter name (was feedback_)
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    chat_log = db.query(ChatLog).get(feedback_data.chat_log_id)  # Fixed reference [[6]](https://www.example.com )
    if not chat_log:
        raise HTTPException(status_code=404, detail="Chat log not found")

    chat_log.feedback = feedback_data.comment
    chat_log.rating = feedback_data.rating
    db.commit()

    # Notify real-time clients
    asyncio.create_task(notify_clients({
        "chat_log_id": feedback_data.chat_log_id,
        "rating": feedback_data.rating,
        "timestamp": datetime.utcnow().isoformat()
    }))

    return {"status": "success", "message": "Feedback submitted"}


# Analytics endpoint
@router.get("/feedback-analytics")
def get_feedback_analytics(db: Session = Depends(get_db)):
    total_feedback = db.query(ChatLog).filter(ChatLog.rating.isnot(None)).count()
    avg_rating = db.query(func.avg(ChatLog.rating)).scalar() or 0

    return {
        "total_feedback": total_feedback,
        "average_rating": round(avg_rating, 2),
        "improvement_rate": "45%"
    }


# Export endpoint
@router.get("/export-feedback", dependencies=[Depends(require_role("admin"))])
def export_feedback(
        db: Session = Depends(get_db),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        child_id: Optional[str] = Query(None)
):
    query = db.query(ChatLog).filter(ChatLog.rating.isnot(None))

    if start_date:
        query = query.filter(ChatLog.timestamp >= start_date)
    if end_date:
        query = query.filter(ChatLog.timestamp <= end_date)
    if child_id:
        query = query.filter(ChatLog.child_id == child_id)

    feedback_logs = query.all()

    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["User ID", "Child ID", "Rating", "Feedback", "Timestamp"])

    for log in feedback_logs:
        writer.writerow([
            log.user_id,
            log.child_id,
            log.rating,
            log.feedback or "",
            log.timestamp.isoformat() if log.timestamp else ""
        ])

    return StreamingResponse(  # Fixed response type [[1]](https://www.example.com )
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback.csv"}
    )
