from __future__ import annotations
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class RedactionConfig:
    redact_emails: bool = True
    redact_phones: bool = True
    redact_tax_ids: bool = True
    redact_doc_numbers: bool = True


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(\+?\d{1,3}[- ]?)?\d{10}\b")
TAXID_RE = re.compile(r"\b([A-Z]{5}\d{4}[A-Z]{1})\b|\b(\d{3}-\d{2}-\d{4})\b")
DOCNUM_RE = re.compile(r"\b[A-Z0-9]{7,14}\b")


def redact_text(text: str, cfg: RedactionConfig = RedactionConfig()) -> str:
    out = text

    if cfg.redact_emails:
        out = EMAIL_RE.sub("[REDACTED_EMAIL]", out)

    if cfg.redact_phones:
        out = PHONE_RE.sub("[REDACTED_PHONE]", out)

    if cfg.redact_tax_ids:
        out = TAXID_RE.sub("[REDACTED_TAX_ID]", out)

    if cfg.redact_doc_numbers:
        out = DOCNUM_RE.sub("[REDACTED_DOC_NO]", out)

    return out
