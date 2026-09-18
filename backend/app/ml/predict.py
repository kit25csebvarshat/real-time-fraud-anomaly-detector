import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from app.ml.train import FEATURE_COLUMNS, MODEL_PATH
from app.services.permission_engine import get_permission_info

_model = None

def load_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            try:
                _model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Warning: Failed to load ML model from {MODEL_PATH}: {e}")
    return _model

def extract_features(
    requested_permissions: List[str],
    developer_verified: bool,
    developer_age_days: int,
    app_age_days: int,
    user_count: int,
    purpose_mismatches_count: int,
    suspicious_combos_count: int
) -> pd.DataFrame:
    perm_set = set(requested_permissions)

    permission_count = len(requested_permissions)
    sensitive_permission_count = sum(
        1 for p in requested_permissions if get_permission_info(p)["sensitivity"] in ["HIGH", "CRITICAL"]
    )

    feature_dict = {
        "permission_count": permission_count,
        "sensitive_permission_count": sensitive_permission_count,
        "email_read": 1 if ("gmail.read" in perm_set or "mail.read" in perm_set) else 0,
        "email_send": 1 if ("gmail.send" in perm_set or "mail.send" in perm_set) else 0,
        "file_read": 1 if ("drive.read" in perm_set or "files.read" in perm_set) else 0,
        "file_write": 1 if ("drive.write" in perm_set or "files.write" in perm_set) else 0,
        "calendar_read": 1 if "calendar.read" in perm_set else 0,
        "calendar_write": 1 if "calendar.write" in perm_set else 0,
        "contacts_read": 1 if "contacts.read" in perm_set else 0,
        "contacts_write": 1 if "contacts.write" in perm_set else 0,
        "admin_access": 1 if ("admin.access" in perm_set or "account.modify" in perm_set) else 0,
        "developer_verified": 1 if developer_verified else 0,
        "developer_age": developer_age_days,
        "application_age": app_age_days,
        "user_count": user_count,
        "purpose_permission_mismatch": purpose_mismatches_count,
        "suspicious_permission_combination": suspicious_combos_count
    }

    return pd.DataFrame([feature_dict])[FEATURE_COLUMNS]

def predict_ml_risk_score(
    requested_permissions: List[str],
    developer_verified: bool,
    developer_age_days: int,
    app_age_days: int,
    user_count: int,
    purpose_mismatches_count: int,
    suspicious_combos_count: int
) -> float:
    clf = load_model()
    df_features = extract_features(
        requested_permissions,
        developer_verified,
        developer_age_days,
        app_age_days,
        user_count,
        purpose_mismatches_count,
        suspicious_combos_count
    )

    if clf is not None:
        try:
            # Predict class probabilities [LOW, MEDIUM, HIGH, CRITICAL]
            probs = clf.predict_proba(df_features)[0]
            # Weighted average mapping probabilities to 0-100 risk scale
            # LOW=10, MEDIUM=37, HIGH=62, CRITICAL=88
            weights = np.array([10.0, 37.0, 62.0, 88.0])
            ml_score = float(np.dot(probs, weights))

            # Add dynamic variance based on mismatch density
            ml_score += purpose_mismatches_count * 3.5
            ml_score += suspicious_combos_count * 4.0
            return float(min(100.0, max(0.0, ml_score)))
        except Exception as e:
            print(f"Error during ML prediction: {e}")

    # Fallback calculation if model artifact isn't loaded
    fallback_score = 15.0
    fallback_score += len(requested_permissions) * 4.0
    fallback_score += purpose_mismatches_count * 15.0
    fallback_score += suspicious_combos_count * 18.0
    if not developer_verified:
        fallback_score += 10.0
    if app_age_days < 30:
        fallback_score += 12.0
    return float(min(100.0, max(0.0, fallback_score)))
