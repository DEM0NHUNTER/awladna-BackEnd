from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from BackEnd.Models.user import User
from BackEnd.Models.child_profile import ChildProfile
from BackEnd.Models.recommendation import Recommendation
from BackEnd.Schemas.child_profile import ChildProfileCreate, ChildProfileResponse
from BackEnd.Utils.database import get_db
from BackEnd.Utils.auth_utils import get_current_user
from BackEnd.Utils.recommendation_generator import (
    generate_recommendations_from_behavior,
    generate_recommendations_from_emotion
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Child Profiles"])


@router.post("/", response_model=ChildProfileResponse)
def create_child_profile(
    profile_data: ChildProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new child profile"""
    new_profile = ChildProfile(
        user_id=current_user.user_id,
        name=profile_data.name,
        birth_date=profile_data.birth_date,
        gender=profile_data.gender,
    )

    new_profile.set_behavioral_data(profile_data.behavioral_patterns)
    new_profile.set_emotional_data(profile_data.emotional_state)

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    try:
        behavior_recs = generate_recommendations_from_behavior(profile_data.behavioral_patterns)
        emotion_recs = generate_recommendations_from_emotion(profile_data.emotional_state)
        for rec in behavior_recs + emotion_recs:
            db.add(Recommendation(child_id=new_profile.child_id, **rec))
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to generate recommendations: {e}")

    return ChildProfileResponse(
        child_id=new_profile.child_id,
        user_id=new_profile.user_id,
        name=new_profile.name,
        age=new_profile.age,
        gender=new_profile.gender,
        behavioral_patterns=new_profile.get_behavioral_data(safe=True),
        emotional_state=new_profile.get_emotional_data(safe=True),
        created_at=new_profile.created_at,
    )


@router.get("/", response_model=List[ChildProfileResponse])
def get_all_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all child profiles for the current user"""
    profiles = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.user_id).all()

    return [
        ChildProfileResponse(
            child_id=p.child_id,
            user_id=p.user_id,
            name=p.name,
            age=p.age,
            gender=p.gender,
            behavioral_patterns=p.get_behavioral_data(safe=True),
            emotional_state=p.get_emotional_data(safe=True),
            created_at=p.created_at,
        )
        for p in profiles
    ]


@router.get("/{child_id}", response_model=ChildProfileResponse)
def get_single_profile(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a specific child profile"""
    profile = db.query(ChildProfile).filter(
        ChildProfile.child_id == child_id,
        ChildProfile.user_id == current_user.user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    return ChildProfileResponse(
        child_id=profile.child_id,
        user_id=profile.user_id,
        name=profile.name,
        age=profile.age,
        gender=profile.gender,
        behavioral_patterns=profile.get_behavioral_data(safe=True),
        emotional_state=profile.get_emotional_data(safe=True),
        created_at=profile.created_at,
    )


@router.put("/{child_id}", response_model=ChildProfileResponse)
def update_child_profile(
    child_id: int,
    update_data: ChildProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a child profile"""
    profile = db.query(ChildProfile).filter(
        ChildProfile.child_id == child_id,
        ChildProfile.user_id == current_user.user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    profile.name = update_data.name
    profile.birth_date = update_data.birth_date
    profile.gender = update_data.gender
    profile.set_behavioral_data(update_data.behavioral_patterns)
    profile.set_emotional_data(update_data.emotional_state)

    db.commit()
    db.refresh(profile)

    return ChildProfileResponse(
        child_id=profile.child_id,
        user_id=profile.user_id,
        name=profile.name,
        age=profile.age,
        gender=profile.gender,
        behavioral_patterns=profile.get_behavioral_data(safe=True),
        emotional_state=profile.get_emotional_data(safe=True),
        created_at=profile.created_at,
    )


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child_profile(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a child profile"""
    profile = db.query(ChildProfile).filter(
        ChildProfile.child_id == child_id,
        ChildProfile.user_id == current_user.user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    db.delete(profile)
    db.commit()
