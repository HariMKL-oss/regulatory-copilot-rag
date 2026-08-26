"""
Role-Based Access Control (RBAC) Zero-Leakage Test Suite for Regulatory Copilot RAG.
"""

import sys
import os
import pytest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from document_parser import RegulatoryDocumentParser
from rbac_engine import RBACPolicyEngine
from vector_store import HybridRegulatoryStore


@pytest.fixture
def indexed_store():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_regulations")
    parser = RegulatoryDocumentParser()
    chunks = parser.parse_directory(data_dir)
    store = HybridRegulatoryStore()
    store.index_chunks(chunks)
    return store


def test_junior_analyst_cannot_retrieve_restricted_credit(indexed_store):
    # Query asking about Restricted Credit Underwriting
    query = "What is the maximum Loan-to-Value (LTV) ratio for multifamily properties?"
    
    # Query as JUNIOR_ANALYST
    results_junior = indexed_store.hybrid_search(query, user_role="JUNIOR_ANALYST", top_k=5)
    for res in results_junior:
        assert res["classification"] != "RESTRICTED_CREDIT_POLICY"
        assert res["doc_id"] != "POL-CREDIT-UW-012"

    # Query as CHIEF_CREDIT_OFFICER
    results_cco = indexed_store.hybrid_search(query, user_role="CHIEF_CREDIT_OFFICER", top_k=5)
    assert len(results_cco) > 0
    assert results_cco[0]["doc_id"] == "POL-CREDIT-UW-012"


def test_senior_risk_officer_cannot_retrieve_aml_sar_confidential(indexed_store):
    query = "What is the mandatory filing deadline for a Suspicious Activity Report (SAR)?"
    
    # Query as SENIOR_RISK_OFFICER (Only Public and Internal Risk)
    results_risk = indexed_store.hybrid_search(query, user_role="SENIOR_RISK_OFFICER", top_k=5)
    for res in results_risk:
        assert res["classification"] != "CONFIDENTIAL_COMPLIANCE"
        assert res["doc_id"] != "POL-AML-CDD-009"

    # Query as COMPLIANCE_AUDITOR
    results_auditor = indexed_store.hybrid_search(query, user_role="COMPLIANCE_AUDITOR", top_k=5)
    assert len(results_auditor) > 0
    assert results_auditor[0]["doc_id"] == "POL-AML-CDD-009"
