VALID_STATES = {
    "DRAFT",
    "SUBMITTED",
    "VALIDATING",
    "ACTION_REQUIRED",
    "VALIDATED",
    "READY_FOR_REVIEW",
    "IN_REVIEW",
    "APPROVED",
    "REJECTED",
    "CLOSED",
}

ALLOWED_TRANSITIONS = {
    "DRAFT": {"SUBMITTED"},
    "SUBMITTED": {"VALIDATING"},
    "VALIDATING": {"ACTION_REQUIRED", "VALIDATED"},
    "ACTION_REQUIRED": {"VALIDATING"},
    "VALIDATED": {"READY_FOR_REVIEW"},
    "READY_FOR_REVIEW": {"IN_REVIEW"},
    "IN_REVIEW": {"APPROVED", "REJECTED"},
    "APPROVED": {"CLOSED"},
    "REJECTED": {"CLOSED"},
}


def can_transition(from_state: str, to_state: str) -> bool:
    return to_state in ALLOWED_TRANSITIONS.get(from_state, set())
