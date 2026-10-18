from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.database import get_db
from app.schemas.schemas import HealthCheckResponse, HealthCheckServices

router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    # Check DB
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    nebius_configured = bool(settings.NEBIUS_API_KEY)
    tavily_configured = bool(settings.TAVILY_API_KEY)

    return HealthCheckResponse(
        status="ok",
        version=settings.VERSION,
        demo_mode=settings.DEMO_MODE,
        services=HealthCheckServices(
            database=db_ok,
            nebius_configured=nebius_configured,
            tavily_configured=tavily_configured,
            email_provider=settings.EMAIL_PROVIDER
        )
    )
