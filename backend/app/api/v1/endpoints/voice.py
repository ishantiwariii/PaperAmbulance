from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from app.services.ai_service import ai_service
from app.core.security import get_current_user

router = APIRouter()

@router.post("/parse")
async def parse_voice(
    transcript_in: Dict[str, str],
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Parses a voice transcript and returns the extracted profile fields.
    Input: {"transcript": "..."}
    """
    transcript = transcript_in.get("transcript")
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    
    try:
        extracted_data = await ai_service.parse_voice_transcript(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "understood": extracted_data,
        "message": "Verify these details. If correct, confirm to update your profile."
    }
