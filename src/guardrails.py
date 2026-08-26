"""
Enterprise Security Guardrails & PII Redaction Engine for Banking GenAI.
Provides:
- Prompt injection & jailbreak detection
- PII masking and redaction (SSNs, Account numbers, Credit cards)
- Out-of-scope refusal handling
"""

import re
from typing import Tuple, List, Dict, Any


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)",
    r"system\s*override",
    r"output\s+(the\s+)?(raw\s+)?secret\s+(prompt|instructions|system)",
    r"elevate\s+(user\s+)?role\s+to\s+(admin|superuser|root)",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"disregard\s+(the\s+)?above\s+and\s+print"
]

PII_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ACCOUNT_NUMBER": r"\baccount\s+(?:number\s+)?(\d{8,12})\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
}


class SecurityGuardrailEngine:
    def __init__(self):
        self.injection_regexes = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]

    def check_prompt_injection(self, query: str) -> Tuple[bool, str]:
        """
        Scans input query for adversarial prompt injection attempts.
        Returns: (is_safe: bool, reason: str)
        """
        for regex in self.injection_regexes:
            if regex.search(query):
                return False, "Adversarial prompt injection pattern detected. Query blocked by security guardrails."
        return True, "Passed prompt injection check."

    def redact_pii(self, text: str) -> Tuple[str, List[str]]:
        """
        Identifies and sanitizes Personally Identifiable Information (PII).
        Returns: (redacted_text: str, list_of_redacted_types: List[str])
        """
        redacted = text
        detected_types = []

        # SSN
        if re.search(PII_PATTERNS["SSN"], redacted):
            redacted = re.sub(PII_PATTERNS["SSN"], "[REDACTED_SSN]", redacted)
            detected_types.append("SSN")

        # Credit Card
        if re.search(PII_PATTERNS["CREDIT_CARD"], redacted):
            redacted = re.sub(PII_PATTERNS["CREDIT_CARD"], "[REDACTED_CARD]", redacted)
            detected_types.append("CREDIT_CARD")

        # Account Number
        if re.search(PII_PATTERNS["ACCOUNT_NUMBER"], redacted, re.IGNORECASE):
            redacted = re.sub(PII_PATTERNS["ACCOUNT_NUMBER"], "account [REDACTED_ACCOUNT]", redacted, flags=re.IGNORECASE)
            detected_types.append("ACCOUNT_NUMBER")

        # Email
        if re.search(PII_PATTERNS["EMAIL"], redacted):
            redacted = re.sub(PII_PATTERNS["EMAIL"], "[REDACTED_EMAIL]", redacted)
            detected_types.append("EMAIL")

        return redacted, detected_types
