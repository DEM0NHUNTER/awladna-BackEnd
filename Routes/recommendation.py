from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from BackEnd.Models.user import User
from BackEnd.Models.recommendation import Recommendation, RecommendationSource, RecommendationPriority
from BackEnd.Models.child_profile import ChildProfile
from BackEnd.Utils.auth_utils import get_current_user
from BackEnd.Utils.database import get_db
from BackEnd.Schemas.child_profile import RecommendationBase, RecommendationUpdate

router = APIRouter(tags=["Recommendations"])


@router.post("/", response_model=RecommendationBase)
def create_recommendation(
        recommendation: RecommendationBase,
        child_id: int = Query(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Ownership check
    child = db.query(ChildProfile).filter(
        ChildProfile.child_id == child_id,
        ChildProfile.user_id == current_user.user_id
    ).first()
    if not child:
        raise HTTPException(status_code=403, detail="Not authorized")

    rec = Recommendation(
        child_id=child_id,
        title=recommendation.title,
        description=recommendation.description,
        source=recommendation.source,
        priority=recommendation.priority,
        effective_date=recommendation.effective_date,
        expiration_date=recommendation.expiration_date,
        type=recommendation.type,
        metadata=recommendation.metadata
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/", response_model=List[RecommendationBase])
def get_recommendations(
        child_id: int = Query(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return db.query(Recommendation).join(ChildProfile).filter(
        Recommendation.child_id == child_id,
        ChildProfile.user_id == current_user.user_id
    ).order_by(Recommendation.created_at.desc()).all()


@router.put("/{rec_id}", response_model=RecommendationBase)
def update_recommendation(
        rec_id: int,
        update_data: RecommendationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    rec = db.query(Recommendation).join(ChildProfile).filter(
        Recommendation.id == rec_id,
        ChildProfile.user_id == current_user.user_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(rec, field, value)

    db.commit()
    db.refresh(rec)
    return rec


@router.delete("/{rec_id}", status_code=204)
def delete_recommendation(
        rec_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    rec = db.query(Recommendation).join(ChildProfile).filter(
        Recommendation.id == rec_id,
        ChildProfile.user_id == current_user.user_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    db.delete(rec)
    db.commit()
