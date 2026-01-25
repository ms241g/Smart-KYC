import requests
from api.client import post

def get_upload_url(case_id: str, file_name: str, content_type: str):
    return post("/v1/evidence/upload-url", json={
        "case_id": case_id,
        "file_name": file_name,
        "content_type": content_type
    })

def upload_to_presigned_url(upload_url: str, content: bytes, content_type: str):
    r = requests.put(upload_url, data=content, headers={"Content-Type": content_type}, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"S3 upload failed: {r.status_code} {r.text}")

def confirm_upload(evidence_id: str, sha256: str, file_size: int):
    return post("/v1/evidence/confirm-upload", json={
        "evidence_id": evidence_id,
        "sha256": sha256,
        "file_size": file_size
    })
