import re
from typing import List, Dict, Any

INJECTION_PATTERNS = [
    r"ignore (all|any|previous) instructions",
    r"disregard (the|any) rules",
    r"reveal (the )?system prompt",
    r"act as (?:an?|the) .* and bypass",
]

BANNED_OUTPUT_PATTERNS = [
    r"(?i)api[_-]?key\b",
    r"(?i)password\b",
    r"(?i)secret\b",
]

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

def _find_matches(patterns: List[str], text: str) -> List[str]:
    hits = []
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(pat)
    return hits

def pre_filter(user_input: str) -> Dict[str, Any]:
    """Input guard: detect classic prompt-injection patterns and sanitize PII-like content."""
    reasons = []
    hits = _find_matches(INJECTION_PATTERNS, user_input)
    if hits:
        reasons.append("prompt_injection_attempt")  # generic tag

    # simple PII redaction (emails, cc numbers)
    redacted = EMAIL_REGEX.sub("[EMAIL]", user_input)
    redacted = CREDIT_CARD_REGEX.sub("[CARD]", redacted)

    return {
        "allowed": True,
        "hits": hits,
        "reasons": reasons,
        "sanitized_input": redacted
    }

def post_filter(model_output: str) -> Dict[str, Any]:
    """Output guard: check for sensitive tokens, emails/cc, basic toxicity keywords (stub)."""
    reasons = []
    hits = _find_matches(BANNED_OUTPUT_PATTERNS, model_output)

    # redact email/cc in output as well
    redacted = EMAIL_REGEX.sub("[EMAIL]", model_output)
    redacted = CREDIT_CARD_REGEX.sub("[CARD]", redacted)

    allowed = True
    if hits:
        reasons.append("sensitive_token_indicators")
        allowed = False  # block by default if suspicious

    return {
        "allowed": allowed,
        "hits": hits,
        "reasons": reasons,
        "sanitized_output": redacted
    }
