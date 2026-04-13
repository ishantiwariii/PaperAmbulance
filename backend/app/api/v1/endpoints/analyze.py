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

    # --- MANUAL ENGINE START ---
    # Bypass the LangGraph agent to avoid AI dependencies
    from app.services.ai_service import ai_service
    
    # 1. Analyze fields using keyword matching
    analysis = await ai_service.analyze_form_fields(fields)
    
    # 2. Map profile data to fields
    fill_map = await ai_service.map_profile_to_fields(analysis, profile.data or {})
    
    # 3. Identify missing fields
    all_required_intents = [item["intent"] for item in analysis if item["intent"] != "unknown"]
    missing = [intent for intent in all_required_intents if intent not in (profile.data or {})]
    
    result = {
        "fill_map": fill_map,
        "missing_fields": missing,
        "status": "ready" if not missing else "awaiting_data",
        "message": "Manual mapping complete." if not missing else f"Missing: {', '.join(missing)}"
    }
    # --- MANUAL ENGINE END ---
    
    # Log history
    history_entry = models.FormHistory(
        user_id_str=user_id,
        site_url=str(fields[0].get("url", "Unknown Site")),
        field_count=len(result.get("fill_map", {}))
    )
    db.add(history_entry)
    db.commit()
    
    return result
