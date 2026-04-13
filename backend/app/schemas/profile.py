from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ProfileBase(BaseModel):
    data: Optional[Dict[str, Any]] = None

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileUpdate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
