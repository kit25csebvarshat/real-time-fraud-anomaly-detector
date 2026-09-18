from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="security_admin")
    created_at = Column(DateTime, default=datetime.utcnow)

class OAuthApp(Base):
    __tablename__ = "oauth_apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    developer = Column(String, nullable=False)
    developer_verified = Column(Boolean, default=False)
    declared_purpose = Column(Text, nullable=False)
    app_age_days = Column(Integer, default=30)
    user_count = Column(Integer, default=100)
    category = Column(String, default="Productivity")
    status = Column(String, default="ACTIVE") # ACTIVE, TRUSTED, REVIEW, REVOKED
    requested_permissions = Column(JSON, nullable=False) # List of permission scope strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scanned = Column(DateTime, nullable=True)

    scans = relationship("RiskScan", back_populates="app", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="app", cascade="all, delete-orphan")

class RiskScan(Base):
    __tablename__ = "risk_scans"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("oauth_apps.id"), nullable=False)
    rule_score = Column(Float, nullable=False)
    ml_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    major_risk_factors = Column(JSON, nullable=False) # List of string descriptions
    purpose_mismatches = Column(JSON, nullable=False) # List of objects
    suspicious_combinations = Column(JSON, nullable=False) # List of objects
    potential_impact = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    app = relationship("OAuthApp", back_populates="scans")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_email = Column(String, nullable=False)
    app_id = Column(Integer, ForeignKey("oauth_apps.id"), nullable=True)
    app_name = Column(String, nullable=False)
    action = Column(String, nullable=False) # MARK_TRUSTED, MARK_REVIEW, REVOKE_ACCESS, PERMISSION_SIMULATION, RESCAN, ADD_APP
    previous_risk = Column(Float, nullable=True)
    current_risk = Column(Float, nullable=True)
    previous_status = Column(String, nullable=True)
    current_status = Column(String, nullable=True)
    reason = Column(Text, nullable=False)

    app = relationship("OAuthApp", back_populates="audit_logs")
