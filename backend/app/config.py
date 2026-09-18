import os

class Settings:
    PROJECT_NAME: str = "OAuthGuard API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # JWT Auth Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "oauthguard-super-secret-security-key-2026-hackathon")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Risk Scoring Configuration
    WEIGHT_RULE: float = 0.6
    WEIGHT_ML: float = 0.4
    
    # Risk Thresholds
    THRESH_LOW_MAX: float = 24.0
    THRESH_MEDIUM_MAX: float = 49.0
    THRESH_HIGH_MAX: float = 74.0
    # > 74.0 is CRITICAL
    
    # Database
    DATABASE_URL: str = "sqlite:///./oauthguard.db"

settings = Settings()
