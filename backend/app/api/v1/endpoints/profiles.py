from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.schemas import profile as profile_schema
from app.core.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=profile_schema.Profile)
def read_profile_me(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get current logged-in user's profile.
    """
    user_id = current_user.get("sub") # Clerk use 'sub' for user ID
    profile = db.query(models.Profile).filter(models.Profile.user_id_str == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )
    return profile

@router.post("/me", response_model=profile_schema.Profile)
def update_or_create_profile_me(
    *,
    db: Session = Depends(get_db),
    profile_in: profile_schema.ProfileBase,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Create or update current user's profile.
    """
    user_id = current_user.get("sub")
    profile = db.query(models.Profile).filter(models.Profile.user_id_str == user_id).first()
    
    if profile:
        # Update
        if profile_in.data is not None:
            profile.data = profile_in.data
    else:
        # Create
        profile = models.Profile(
            user_id_str=user_id,
            data=profile_in.data
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile
