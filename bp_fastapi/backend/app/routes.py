from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import db, models, schemas, telemetry
from datetime import datetime
from typing import List

router = APIRouter()

def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()

def calculate_category(systolic: int, diastolic: int) -> str:
    # Hypertensive crisis first (as spec says treat >= thresholds inclusive; crisis if >180 or >120)
    if systolic > 180 or diastolic > 120:
        return "High blood pressure (Hypertensive crisis)"

    if systolic >= 140 or diastolic >= 90:
        return "High blood pressure"

    if (130 <= systolic < 140) or (80 <= diastolic < 90):
        return "Pre-High blood pressure"

    # Ideal: use common bounds: systolic 90..119 and diastolic 60..79 (both inclusive lower)
    if 90 <= systolic < 120 and 60 <= diastolic < 80:
        return "Ideal blood pressure"

    # Low
    if systolic < 90 or diastolic < 60:
        return "Low blood pressure"

    # fallback 
    return "Ideal blood pressure"

@router.post("/api/calculate", response_model=schemas.ReadingOut, status_code=201)
def api_calculate(req: schemas.CalculateRequest, db_sess: Session = Depends(get_db)):
    # Validate systolic > diastolic
    if req.systolic <= req.diastolic:
        raise HTTPException(status_code=400, detail="Systolic must be greater than diastolic.")

    category = calculate_category(req.systolic, req.diastolic)

    r = models.Reading(
        systolic=req.systolic,
        diastolic=req.diastolic,
        category=category
    )
    db_sess.add(r)
    db_sess.commit()
    db_sess.refresh(r)

    # Telemetry: event + metric
    telemetry.track_event("BP_Calculated", properties={
        "systolic": str(req.systolic),
        "diastolic": str(req.diastolic),
        "category": category
    })
    telemetry.track_metric("systolic", req.systolic)
    telemetry.track_metric("diastolic", req.diastolic)

    return r

@router.get("/api/history", response_model=List[schemas.ReadingOut])
def api_history(limit: int = 20, db_sess: Session = Depends(get_db)):
    rows = db_sess.query(models.Reading).order_by(models.Reading.created_at.desc()).limit(limit).all()
    return rows

@router.delete("/api/history/{reading_id}", status_code=200)
def api_delete(reading_id: int, db_sess: Session = Depends(get_db)):
    r = db_sess.query(models.Reading).get(reading_id)
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db_sess.delete(r)
    db_sess.commit()
    telemetry.track_event("BP_Deleted", properties={"id": str(reading_id)})
    return {"status": "deleted"}
