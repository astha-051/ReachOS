import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
import app.models  # Ensure all SQLAlchemy models are registered before create_all

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ReachOS - AI Lead Intelligence, Qualification & Personalized Outreach Platform"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.api import health, campaigns, leads, research, outreach, replies, analytics

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["Campaigns"])
app.include_router(leads.router, prefix=f"{settings.API_V1_STR}/leads", tags=["Leads"])
app.include_router(research.router, prefix=settings.API_V1_STR, tags=["Research"])
app.include_router(outreach.router, prefix=settings.API_V1_STR, tags=["Outreach & Qualification"])
app.include_router(replies.router, prefix=settings.API_V1_STR, tags=["Reply Intelligence"])
app.include_router(analytics.router, prefix=settings.API_V1_STR, tags=["Analytics"])

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
