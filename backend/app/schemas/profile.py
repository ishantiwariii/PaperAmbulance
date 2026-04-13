from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ProfileBase(BaseModel):
    data: Optional[Dict[str, Any]] = None

class ProfileCreate(ProfileBase):
    user_id_str: str

class ProfileUpdate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: Optional[int] = None
    user_id_str: str
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
