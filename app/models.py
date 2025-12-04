from pydantic import BaseModel
from typing import Optional


class OCRResponse(BaseModel):
    success: bool
    text: str
    language: Optional[str] = "vi"
    error: Optional[str] = None

