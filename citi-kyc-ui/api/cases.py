from api.client import post, get

def initiate_case(customer_id: str, category_id: str):
    return post("/v1/cases/initiate", json={"customer_id": customer_id, "category_id": category_id})

def submit_case(case_id: str, customer_details: dict, evidence_ids: list, consent: bool, idempotency_key: str):
    headers = {"Idempotency-Key": idempotency_key}
    return post(
        f"/v1/cases/{case_id}/submit",
        json={"customer_details": customer_details, "evidence_ids": evidence_ids, "consent": consent},
        headers=headers
    )

def resolve_case(case_id: str, updated_customer_details: dict | None, additional_evidence_ids: list | None):
    payload = {
        "updated_customer_details": updated_customer_details,
        "additional_evidence_ids": additional_evidence_ids
    }
    return post(f"/v1/cases/{case_id}/resolve", json=payload)

def case_status(case_id: str):
    return get(f"/v1/cases/{case_id}/status")

def submit_for_review(case_id: str):
    return post(f"/v1/cases/{case_id}/submit-for-review", json={})
