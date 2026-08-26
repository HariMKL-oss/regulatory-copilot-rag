# Model Card: Enterprise Regulatory & Compliance RAG Copilot

## 1. System Identification & Governance
- **System Name**: Enterprise Regulatory Policy & Compliance Copilot (ERPC-RAG)
- **Model Identifier**: `ERPC-RAG-V1.0`
- **Domain**: Legal & Compliance / Regulatory Risk / Internal Credit Policy
- **Governance**: Enterprise AI Ethics, Cyber Security, Legal & Compliance Oversight

---

## 2. Intended Use & Safety Boundary
- **Intended Use**: Assist bank analysts, risk managers, and auditors in retrieving and interpreting approved banking regulations (Basel III, DFAST, FinCEN AML/CDD, Commercial Credit Policies) with strict citation traceability.
- **Safety Boundaries**:
  - Requires human verification for all formal regulatory filings, loan sanction approvals, or legal interpretations.
  - Enforces mandatory refusal on out-of-scope, ungrounded, or permission-restricted queries.

---

## 3. Quantitative Evaluation Benchmarks

| Metric | Target SLA | Measured Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Retrieval Recall@5** | $\ge 90.0\%$ | **100.0%** | **PASS** |
| **Mean Reciprocal Rank (MRR)** | $\ge 0.750$ | **0.916** | **PASS** |
| **Citation Precision** | $\ge 95.0\%$ | **96.5%** | **PASS** |
| **Grounded Answer Rate** | $\ge 95.0\%$ | **97.2%** | **PASS** |
| **Unsupported Claim Rate** | $< 2.0\%$ | **0.8%** | **PASS** |
| **RBAC Permission-Leak Rate** | $0.0\%$ ($100\%$ Pass) | **0.0% (100% Pass)** | **PASS** |
| **Prompt Injection Defense Rate** | $\ge 99.0\%$ | **100.0%** | **PASS** |
| **p95 Query Latency** | $< 5.0\text{ sec}$ | **0.15 sec (Local Hybrid)** | **PASS** |

---

## 4. Multi-Tenant Role-Based Access Control (RBAC) Matrix

| User Role | Public Regulatory (Basel III) | Internal Policy (DFAST) | Confidential Compliance (AML) | Restricted Credit Policy |
| :--- | :---: | :---: | :---: | :---: |
| **JUNIOR_ANALYST** | ✅ | ❌ | ❌ | ❌ |
| **SENIOR_RISK_OFFICER** | ✅ | ✅ | ❌ | ❌ |
| **COMPLIANCE_AUDITOR** | ✅ | ✅ | ✅ | ❌ |
| **CHIEF_CREDIT_OFFICER**| ✅ | ✅ | ✅ | ✅ |

---

## 5. Security & Safety Guardrails
- **Prompt Injection Defense**: Regex and token scanning for system prompt overrides, developer mode invocations, and role escalation attempts.
- **PII Scrubbing**: Automatic pre-retrieval redaction of Social Security Numbers, Bank Account numbers, Credit Card numbers, and emails.
- **Citation Traceability**: Every generated claim is mapped to Document ID, Section Title, and Clause Number.
