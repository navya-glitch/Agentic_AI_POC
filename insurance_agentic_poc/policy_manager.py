# policy_manager.py
"""
Policy management utilities: storage, renewal, digital wallet, etc.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

POLICIES_DB_PATH = os.path.join(os.path.dirname(__file__), "policies_wallet_db.json")
RENEWALS_DB_PATH = os.path.join(os.path.dirname(__file__), "renewals_db.json")

def get_all_policies(user_email: str = None) -> List[Dict[str, Any]]:
    """Retrieve all active policies for a user (digital wallet)."""
    if not os.path.exists(POLICIES_DB_PATH):
        return []
    try:
        with open(POLICIES_DB_PATH, "r", encoding="utf-8") as f:
            policies = json.load(f)
        if user_email:
            return [p for p in policies if p.get("buyer_email") == user_email]
        return policies
    except:
        return []

def save_policy(policy_data: Dict[str, Any]) -> bool:
    """Save a new policy to wallet."""
    try:
        policies = get_all_policies()
        policy_data["policy_number"] = f"POL-{datetime.utcnow().timestamp()}"
        policy_data["issue_date"] = datetime.utcnow().isoformat()
        policy_data["expiry_date"] = (datetime.utcnow() + timedelta(days=365)).isoformat()
        policy_data["status"] = "Active"
        policies.append(policy_data)
        with open(POLICIES_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(policies, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving policy: {e}")
        return False

def get_renewal_reminders(user_email: str = None) -> List[Dict[str, Any]]:
    """Get upcoming renewal reminders."""
    if not os.path.exists(RENEWALS_DB_PATH):
        return []
    try:
        with open(RENEWALS_DB_PATH, "r", encoding="utf-8") as f:
            reminders = json.load(f)
        if user_email:
            return [r for r in reminders if r.get("buyer_email") == user_email]
        return reminders
    except:
        return []

def create_renewal_reminder(policy_id: str, user_email: str, plan_name: str, expiry_date: str) -> bool:
    """Create a renewal reminder (30 days before expiry)."""
    try:
        reminders = get_renewal_reminders()
        reminder = {
            "policy_id": policy_id,
            "buyer_email": user_email,
            "plan_name": plan_name,
            "expiry_date": expiry_date,
            "reminder_sent": False,
            "created_at": datetime.utcnow().isoformat(),
        }
        reminders.append(reminder)
        with open(RENEWALS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(reminders, f, indent=2)
        return True
    except Exception as e:
        print(f"Error creating renewal reminder: {e}")
        return False

def renew_policy_one_click(policy_id: str) -> Dict[str, Any]:
    """Simulate one-click renewal of a policy."""
    try:
        policies = get_all_policies()
        for policy in policies:
            if policy.get("policy_number") == policy_id:
                old_expiry = datetime.fromisoformat(policy.get("expiry_date", datetime.utcnow().isoformat()))
                new_expiry = old_expiry + timedelta(days=365)
                policy["expiry_date"] = new_expiry.isoformat()
                policy["last_renewed"] = datetime.utcnow().isoformat()
                with open(POLICIES_DB_PATH, "w", encoding="utf-8") as f:
                    json.dump(policies, f, indent=2)
                return {"status": "success", "message": "Policy renewed successfully", "new_expiry": new_expiry.isoformat()}
        return {"status": "error", "message": "Policy not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def download_policy_pdf_mock(policy_id: str) -> str:
    """Generate a mock policy document (in production, use a PDF library)."""
    policies = get_all_policies()
    for policy in policies:
        if policy.get("policy_number") == policy_id:
            content = f"""
INSURANCE POLICY DOCUMENT
==========================

Policy Number: {policy.get('policy_number')}
Plan: {policy.get('plan_name')}
Company: {policy.get('company')}
Holder: {policy.get('buyer_name')}
Email: {policy.get('buyer_email')}

Issue Date: {policy.get('issue_date')}
Expiry Date: {policy.get('expiry_date')}
Status: {policy.get('status')}

Annual Premium: ${policy.get('total_paid_usd', 0):,.2f}
Riders: {', '.join(policy.get('riders', []))}
Auto-Renew: {policy.get('auto_renew', False)}

[This is a mock document. In production, generate a proper PDF.]
"""
            return content
    return ""
