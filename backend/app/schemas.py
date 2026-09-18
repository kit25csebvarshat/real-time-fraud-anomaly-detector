from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = "Security Admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Permission Schemas ---
class PermissionDetail(BaseModel):
    permission: str
    category: str # email, drive, calendar, contacts, admin, profile
    sensitivity: str # LOW, MEDIUM, HIGH, CRITICAL
    purpose_relevance: str # RELEVANT, POTENTIALLY_EXCESSIVE, HIGH_RISK_MISMATCH
    description: str

class SuspiciousCombination(BaseModel):
    combination: List[str]
    title: str
    severity: str # MEDIUM, HIGH, CRITICAL
    explanation: str

class PurposeMismatch(BaseModel):
    permission: str
    classification: str # POTENTIALLY_EXCESSIVE, HIGH_RISK_MISMATCH
    reason: str

# --- OAuth App Schemas ---
class AppBase(BaseModel):
    name: str
    developer: str
    developer_verified: bool = False
    declared_purpose: str
    app_age_days: int = 30
    user_count: int = 100
    category: str = "Productivity"
    requested_permissions: List[str]

class AppCreate(AppBase):
    pass

class AppUpdate(BaseModel):
    name: Optional[str] = None
    developer: Optional[str] = None
    developer_verified: Optional[bool] = None
    declared_purpose: Optional[str] = None
    requested_permissions: Optional[List[str]] = None

class AppResponse(AppBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    last_scanned: Optional[datetime] = None
    current_risk_score: Optional[float] = None
    current_risk_level: Optional[str] = None

    class Config:
        from_attributes = True

# --- Risk & Explanation Schemas ---
class RiskScanResponse(BaseModel):
    id: Optional[int] = None
    app_id: int
    rule_score: float
    ml_score: float
    final_score: float
    risk_level: str
    major_risk_factors: List[str]
    purpose_mismatches: List[PurposeMismatch]
    suspicious_combinations: List[SuspiciousCombination]
    potential_impact: str
    recommended_action: str
    permissions_breakdown: List[PermissionDetail]
    scanned_at: datetime

    class Config:
        from_attributes = True

# --- Simulator Schemas ---
class WhatIfSimulationRequest(BaseModel):
    permissions: List[str]

class WhatIfSimulationResponse(BaseModel):
    app_id: int
    app_name: str
    original_score: float
    new_score: float
    score_delta: float
    original_level: str
    new_level: str
    removed_permissions: List[str]
    risk_factor_changes: List[str]
    simulated_scan: RiskScanResponse

# --- Action Schemas ---
class ActionRequest(BaseModel):
    reason: Optional[str] = "Admin manual override"

# --- Audit Log Schemas ---
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_email: str
    app_id: Optional[int]
    app_name: str
    action: str
    previous_risk: Optional[float]
    current_risk: Optional[float]
    previous_status: Optional[str]
    current_status: Optional[str]
    reason: str

    class Config:
        from_attributes = True

# --- Dashboard Stats Schemas ---
class DashboardStatsResponse(BaseModel):
    total_apps: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    critical_risk_count: int
    apps_requiring_review: int
    risk_distribution: List[Dict[str, Any]]
    top_risk_apps: List[Dict[str, Any]]
    recent_scans: List[Dict[str, Any]]
    recent_actions: List[AuditLogResponse]
    permission_category_distribution: List[Dict[str, Any]]
