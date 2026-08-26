"""
Zero-Trust Role-Based Access Control (RBAC) Engine for Regulatory RAG.
Enforces multi-tenant data governance by restricting document retrieval to
authorized organizational clearance levels.
"""

from typing import List, Set, Dict, Any


ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "JUNIOR_ANALYST": {
        "PUBLIC_REGULATORY"
    },
    "SENIOR_RISK_OFFICER": {
        "PUBLIC_REGULATORY",
        "INTERNAL_BANK_POLICY"
    },
    "COMPLIANCE_AUDITOR": {
        "PUBLIC_REGULATORY",
        "INTERNAL_BANK_POLICY",
        "CONFIDENTIAL_COMPLIANCE"
    },
    "CHIEF_CREDIT_OFFICER": {
        "PUBLIC_REGULATORY",
        "INTERNAL_BANK_POLICY",
        "CONFIDENTIAL_COMPLIANCE",
        "RESTRICTED_CREDIT_POLICY"
    },
    "SYSTEM_ADMIN": {
        "PUBLIC_REGULATORY",
        "INTERNAL_BANK_POLICY",
        "CONFIDENTIAL_COMPLIANCE",
        "RESTRICTED_CREDIT_POLICY"
    }
}


class RBACPolicyEngine:
    def __init__(self, custom_permissions: Dict[str, Set[str]] = None):
        self.permissions = custom_permissions or ROLE_PERMISSIONS

    def is_authorized(self, user_role: str, document_classification: str) -> bool:
        """Checks if a user role is permitted to view a document classification tier."""
        allowed_tiers = self.permissions.get(user_role.upper(), set())
        return document_classification.upper() in allowed_tiers

    def filter_chunks_for_role(self, chunks: List[Any], user_role: str) -> List[Any]:
        """
        Pre-retrieval security filter: Restricts candidate vector corpus
        strictly to chunks the user role is authorized to view.
        Zero permission leakage guarantee.
        """
        allowed_tiers = self.permissions.get(user_role.upper(), set())
        return [c for c in chunks if getattr(c, "classification", "") in allowed_tiers]
