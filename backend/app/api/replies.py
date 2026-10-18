from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import ReplySchema, ReplyAnalysisRequest
from app.services.reply_service import analyze_lead_reply_service

router = APIRouter()

@router.post("/leads/{lead_id}/reply/analyze", response_model=ReplySchema)
def analyze_reply(lead_id: str, req: ReplyAnalysisRequest, db: Session = Depends(get_db)):
    if not req.reply_body or not req.reply_body.strip():
        raise HTTPException(status_code=400, detail="Reply body cannot be empty")

    try:
        reply = analyze_lead_reply_service(
            lead_id=lead_id,
            reply_body=req.reply_body,
            db=db
        )
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reply analysis failed: {str(e)}")
