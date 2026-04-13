from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.services.pdf_service import pdf_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/pdf")
async def export_profile_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Exports the current user's profile as a PDF document.
    """
    user_id = current_user.get("sub")
    profile = db.query(models.Profile).filter(models.Profile.user_id_str == user_id).first()
    
    if not profile or not profile.data:
        raise HTTPException(status_code=404, detail="Profile data not found. Please setup your profile first.")
    
    pdf_buffer = pdf_service.generate_profile_pdf(profile.data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=PaperAmbulance_Profile.pdf"}
    )
