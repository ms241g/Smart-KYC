import uuid

def new_case_id() -> str:
    return f"KYC-{uuid.uuid4().hex[:12].upper()}"
