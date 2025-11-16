from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CalculateRequest(BaseModel):
    systolic: int = Field(..., ge=70, le=190)
    diastolic: int = Field(..., ge=40, le=100)

class ReadingOut(BaseModel):
    id: int
    systolic: int
    diastolic: int
    category: str
    created_at: datetime

    class Config:
        orm_mode = True
