import pandas as pd
import numpy as np
import random
from typing import Tuple

def generate_synthetic_dataset(num_samples: int = 1500) -> pd.DataFrame:
    np.random.seed(42)
    random.seed(42)

    data = []

    for _ in range(num_samples):
        # 1. Randomly pick base profile type
        profile_type = random.choices(["safe", "moderate", "excessive", "malicious"], weights=[0.35, 0.30, 0.20, 0.15])[0]

        developer_verified = 1 if profile_type in ["safe", "moderate"] and random.random() > 0.3 else 0
        developer_age = random.randint(180, 1500) if developer_verified else random.randint(5, 120)
        application_age = random.randint(90, 1000) if profile_type == "safe" else random.randint(2, 600)
        user_count = random.randint(1000, 50000) if profile_type == "safe" else random.randint(10, 2000)

        if profile_type == "safe":
            email_read = random.choices([0, 1], weights=[0.8, 0.2])[0]
            email_send = 0
            file_read = random.choices([0, 1], weights=[0.7, 0.3])[0]
            file_write = 0
            calendar_read = random.choices([0, 1], weights=[0.6, 0.4])[0]
            calendar_write = random.choices([0, 1], weights=[0.8, 0.2])[0]
            contacts_read = random.choices([0, 1], weights=[0.8, 0.2])[0]
            contacts_write = 0
            admin_access = 0
            purpose_mismatch = random.choices([0, 1], weights=[0.95, 0.05])[0]
            suspicious_combo = 0

        elif profile_type == "moderate":
            email_read = random.choices([0, 1], weights=[0.6, 0.4])[0]
            email_send = random.choices([0, 1], weights=[0.9, 0.1])[0]
            file_read = random.choices([0, 1], weights=[0.5, 0.5])[0]
            file_write = random.choices([0, 1], weights=[0.7, 0.3])[0]
            calendar_read = random.choices([0, 1], weights=[0.5, 0.5])[0]
            calendar_write = random.choices([0, 1], weights=[0.6, 0.4])[0]
            contacts_read = random.choices([0, 1], weights=[0.6, 0.4])[0]
            contacts_write = random.choices([0, 1], weights=[0.8, 0.2])[0]
            admin_access = 0
            purpose_mismatch = random.choices([0, 1, 2], weights=[0.7, 0.25, 0.05])[0]
            suspicious_combo = random.choices([0, 1], weights=[0.85, 0.15])[0]

        elif profile_type == "excessive":
            email_read = random.choices([0, 1], weights=[0.3, 0.7])[0]
            email_send = random.choices([0, 1], weights=[0.6, 0.4])[0]
            file_read = random.choices([0, 1], weights=[0.2, 0.8])[0]
            file_write = random.choices([0, 1], weights=[0.4, 0.6])[0]
            calendar_read = random.choices([0, 1], weights=[0.3, 0.7])[0]
            calendar_write = random.choices([0, 1], weights=[0.4, 0.6])[0]
            contacts_read = random.choices([0, 1], weights=[0.3, 0.7])[0]
            contacts_write = random.choices([0, 1], weights=[0.5, 0.5])[0]
            admin_access = random.choices([0, 1], weights=[0.9, 0.1])[0]
            purpose_mismatch = random.randint(1, 4)
            suspicious_combo = random.randint(1, 2)

        else: # malicious
            email_read = 1
            email_send = random.choices([0, 1], weights=[0.2, 0.8])[0]
            file_read = 1
            file_write = random.choices([0, 1], weights=[0.3, 0.7])[0]
            calendar_read = random.choices([0, 1], weights=[0.4, 0.6])[0]
            calendar_write = random.choices([0, 1], weights=[0.5, 0.5])[0]
            contacts_read = 1
            contacts_write = random.choices([0, 1], weights=[0.5, 0.5])[0]
            admin_access = random.choices([0, 1], weights=[0.5, 0.5])[0]
            purpose_mismatch = random.randint(2, 5)
            suspicious_combo = random.randint(1, 3)

        # Count total and sensitive permissions
        all_perms = [email_read, email_send, file_read, file_write, calendar_read, calendar_write, contacts_read, contacts_write, admin_access]
        permission_count = sum(all_perms) + random.randint(1, 3) # including profile
        sensitive_permission_count = email_read + email_send + file_write + contacts_write + calendar_write + admin_access

        # Rule-based ground truth risk target generation for realistic modeling
        risk_score = 0
        risk_score += sensitive_permission_count * 15
        risk_score += purpose_mismatch * 18
        risk_score += suspicious_combo * 20
        if not developer_verified:
            risk_score += 12
        if application_age < 30:
            risk_score += 15
        if email_read and email_send:
            risk_score += 25
        if admin_access:
            risk_score += 30

        risk_score = min(100, max(0, risk_score))

        if risk_score < 25:
            risk_level = 0 # LOW
        elif risk_score < 50:
            risk_level = 1 # MEDIUM
        elif risk_score < 75:
            risk_level = 2 # HIGH
        else:
            risk_level = 3 # CRITICAL

        data.append({
            "permission_count": permission_count,
            "sensitive_permission_count": sensitive_permission_count,
            "email_read": email_read,
            "email_send": email_send,
            "file_read": file_read,
            "file_write": file_write,
            "calendar_read": calendar_read,
            "calendar_write": calendar_write,
            "contacts_read": contacts_read,
            "contacts_write": contacts_write,
            "admin_access": admin_access,
            "developer_verified": developer_verified,
            "developer_age": developer_age,
            "application_age": application_age,
            "user_count": user_count,
            "purpose_permission_mismatch": purpose_mismatch,
            "suspicious_permission_combination": suspicious_combo,
            "risk_score": risk_score,
            "risk_level": risk_level
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_synthetic_dataset()
    print(f"Generated synthetic dataset with {len(df)} records.")
    print(df["risk_level"].value_counts())
