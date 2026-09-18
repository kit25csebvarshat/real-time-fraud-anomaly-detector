from typing import List, Dict, Any

def generate_explainable_narrative(
    app_name: str,
    declared_purpose: str,
    final_score: float,
    risk_level: str,
    major_risk_factors: List[str],
    purpose_mismatches: List[Dict[str, Any]],
    suspicious_combinations: List[Dict[str, Any]],
    requested_permissions: List[str]
) -> Dict[str, str]:
    perm_set = set(requested_permissions)

    # 1. Potential Impact Synthesis
    impact_items = []

    if "gmail.send" in perm_set or "mail.send" in perm_set:
        impact_items.append("The application could send emails on behalf of employee accounts, potentially enabling internal BEC (Business Email Compromise) or phishing campaigns.")

    if "gmail.read" in perm_set or "mail.read" in perm_set:
        impact_items.append("Sensitive corporate communications, confidential messages, and password reset tokens in user inboxes could be exposed or harvested.")

    if "drive.write" in perm_set or "files.write" in perm_set:
        impact_items.append("Cloud documents could be modified, overwritten, or encrypted (ransomware risk), destroying critical organizational data.")

    if "drive.read" in perm_set or "files.read" in perm_set:
        impact_items.append("Proprietary files, financial records, and employee documents stored in cloud drive could be accessed and exfiltrated.")

    if "admin.access" in perm_set or "account.modify" in perm_set or "user.impersonation" in perm_set:
        impact_items.append("Full organizational domain control or identity impersonation could be achieved, bypassing single sign-on protections.")

    if not impact_items:
        impact_items.append(f"If {app_name} or its developer credentials were compromised, the application could access basic user profile data and low-sensitivity scopes.")

    potential_impact = " ".join(impact_items)

    # 2. Recommended Action Synthesis
    actions = []

    if risk_level in ["CRITICAL", "HIGH"]:
        actions.append(f"1. Immediately review whether {app_name} is essential for employee business operations.")
        if purpose_mismatches:
            unneeded = [m['permission'] for m in purpose_mismatches]
            actions.append(f"2. Consider removing excessive permissions ({', '.join(unneeded)}) using the What-If Simulator before approving access.")
        else:
            actions.append("2. Restrict scope access to read-only permissions where possible.")
        actions.append("3. Verify developer identity and request security compliance documentation (SOC2 / ISO27001).")

    elif risk_level == "MEDIUM":
        actions.append(f"1. Conduct periodic security review of {app_name}'s usage across departments.")
        actions.append("2. Monitor for any unauthorized updates or scope changes requested by the developer.")

    else: # LOW
        actions.append(f"{app_name} requests minimal, relevant permissions matching its declared purpose. Approve standard access with regular audit monitoring.")

    recommended_action = "\n".join(actions)

    return {
        "potential_impact": potential_impact,
        "recommended_action": recommended_action
    }
