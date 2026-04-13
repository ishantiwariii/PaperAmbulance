from typing import Any, List, Dict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.services.agent_service import form_agent
from app.core.security import get_current_user

router = APIRouter()

@router.post("/fill")
async def fill_form(
    fields: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Invokes the LangGraph agent to analyze and process form fields.
    """
    if not fields:
        raise HTTPException(status_code=400, detail="Fields list cannot be empty")
    
    user_id = current_user.get("sub")
    profile = db.query(models.Profile).filter(models.Profile.user_id_str == user_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Run the Agent
    result = await form_agent.run(
        raw_fields=fields, 
        profile_data=profile.data or {}, 
        user_id=user_id
    )
    
    # Log history
    history_entry = models.FormHistory(
        user_id_str=user_id,
        site_url=str(fields[0].get("url", "Unknown Site")),
        field_count=len(result.get("fill_map", {}))
    )
    db.add(history_entry)
    db.commit()
    
    return result
