from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.database import engine, Base
from app.routes import auth_routes, app_routes, dashboard_routes, audit_routes

# Create DB tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered OAuth Risk & Permission Intelligence Platform — Enterprise Security MVP",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development & frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(app_routes.router, prefix=settings.API_PREFIX)
app.include_router(dashboard_routes.router, prefix=settings.API_PREFIX)
app.include_router(audit_routes.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "message": "OAuthGuard Security Intelligence Platform API is running",
        "docs": "/docs",
        "version": settings.VERSION
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
