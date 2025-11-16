from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .db import Base

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    category = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
