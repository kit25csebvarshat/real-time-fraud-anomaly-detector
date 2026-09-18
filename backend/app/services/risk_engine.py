from typing import List, Dict, Any, Tuple
from app.config import settings
from app.services.permission_engine import get_permission_info, analyze_suspicious_combinations
from app.services.purpose_engine import analyze_purpose_permission_fit
from app.ml.predict import predict_ml_risk_score

def calculate_rule_risk_score(
    requested_permissions: List[str],
    developer_verified: bool,
    app_age_days: int,
    user_count: int,
    purpose_mismatches: List[Dict[str, Any]],
    suspicious_combos: List[Dict[str, Any]]
) -> Tuple[float, List[str]]:
    score = 0.0
    major_risk_factors = []

    # 1. Permission Sensitivity Base Score
    for perm in requested_permissions:
        info = get_permission_info(perm)
        sens = info["sensitivity"]
        if sens == "CRITICAL":
            score += 28.0
        elif sens == "HIGH":
            score += 14.0
        elif sens == "MEDIUM":
            score += 6.0
        else: # LOW
            score += 2.0

    # 2. Suspicious Combinations Penalty
    for combo in suspicious_combos:
        severity = combo["severity"]
        title = combo["title"]
        if severity == "CRITICAL":
            score += 25.0
            major_risk_factors.append(f"Suspicious permission combination detected: {title} ({', '.join(combo['combination'])})")
        elif severity == "HIGH":
            score += 15.0
            major_risk_factors.append(f"Suspicious permission combination detected: {title}")

    # 3. Purpose Mismatch Penalty
    high_mismatches = [m for m in purpose_mismatches if m["classification"] == "HIGH_RISK_MISMATCH"]
    excessive_mismatches = [m for m in purpose_mismatches if m["classification"] == "POTENTIALLY_EXCESSIVE"]

    if high_mismatches:
        score += len(high_mismatches) * 16.0
        perm_names = [m['permission'] for m in high_mismatches]
        major_risk_factors.append(f"Requested permissions ({', '.join(perm_names)}) do not align with declared application purpose.")

    if excessive_mismatches:
        score += len(excessive_mismatches) * 6.0

    # 4. Developer Verification Context
    if not developer_verified:
        score += 12.0
        major_risk_factors.append("Developer verification status is unavailable or unverified.")

    # 5. Application Age Context
    if app_age_days < 30:
        score += 14.0
        major_risk_factors.append(f"Recently published application ({app_age_days} days old).")
    elif app_age_days < 90:
        score += 6.0

    # 6. User Base Context
    if user_count < 500 and (len(high_mismatches) > 0 or len(suspicious_combos) > 0):
        score += 8.0
        major_risk_factors.append(f"Unestablished user base ({user_count} users) with elevated access requests.")

    rule_score = float(min(100.0, max(0.0, score)))
    return rule_score, major_risk_factors


def calculate_hybrid_risk_assessment(
    name: str,
    declared_purpose: str,
    category: str,
    developer: str,
    developer_verified: bool,
    app_age_days: int,
    user_count: int,
    requested_permissions: List[str],
    weight_rule: float = None,
    weight_ml: float = None
) -> Dict[str, Any]:
    if weight_rule is None:
        weight_rule = settings.WEIGHT_RULE
    if weight_ml is None:
        weight_ml = settings.WEIGHT_ML

    # 1. Permission-Purpose Fit Analysis
    permissions_breakdown, purpose_mismatches = analyze_purpose_permission_fit(
        declared_purpose, category, requested_permissions
    )

    # 2. Suspicious Permission Combination Analysis
    suspicious_combos = analyze_suspicious_combinations(requested_permissions)

    # 3. Rule Score Calculation
    rule_score, major_risk_factors = calculate_rule_risk_score(
        requested_permissions,
        developer_verified,
        app_age_days,
        user_count,
        purpose_mismatches,
        suspicious_combos
    )

    # 4. ML Score Prediction
    ml_score = predict_ml_risk_score(
        requested_permissions=requested_permissions,
        developer_verified=developer_verified,
        developer_age_days=app_age_days * 2, # heuristic
        app_age_days=app_age_days,
        user_count=user_count,
        purpose_mismatches_count=len(purpose_mismatches),
        suspicious_combos_count=len(suspicious_combos)
    )

    # 5. Hybrid Final Score
    final_score = float(round(weight_rule * rule_score + weight_ml * ml_score, 1))
    final_score = min(100.0, max(0.0, final_score))

    # 6. Classification into Risk Level
    if final_score <= settings.THRESH_LOW_MAX:
        risk_level = "LOW"
    elif final_score <= settings.THRESH_MEDIUM_MAX:
        risk_level = "MEDIUM"
    elif final_score <= settings.THRESH_HIGH_MAX:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return {
        "rule_score": round(rule_score, 1),
        "ml_score": round(ml_score, 1),
        "final_score": final_score,
        "risk_level": risk_level,
        "major_risk_factors": major_risk_factors,
        "purpose_mismatches": purpose_mismatches,
        "suspicious_combinations": suspicious_combos,
        "permissions_breakdown": permissions_breakdown
    }
