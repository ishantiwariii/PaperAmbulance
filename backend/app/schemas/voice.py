from pydantic import BaseModel

class VoiceParseRequest(BaseModel):
    transcript: str
