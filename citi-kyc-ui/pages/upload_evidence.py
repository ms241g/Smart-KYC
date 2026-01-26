import streamlit as st
import hashlib
from api import evidence
from core.ui_components import render_compliance_notice

CONTENT_TYPE_MAP = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def render():
    st.subheader("📎 Upload Evidence")
    render_compliance_notice()

    case_id = st.session_state.get("case_id")
    if not case_id:
        st.warning("Initiate a case first.")
        return

    req = st.session_state.get("requirements", {})
    allowed_doc_types = req.get("required_documents", [])
    st.markdown("### Allowed Document Types (Policy)")
    st.write(allowed_doc_types)

    uploaded_files = st.file_uploader(
        "Upload evidence (PDF/JPG/PNG/DOC/DOCX)",
        type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
        accept_multiple_files=True
    )

    if st.button("Upload Selected Files 🚀", disabled=not uploaded_files):
        for f in uploaded_files:
            ext = f.name.split(".")[-1].lower()
            content_type = CONTENT_TYPE_MAP.get(ext, "application/octet-stream")
            content = f.getvalue()
            file_hash = _sha256(content)

            # 1) Presigned URL
            print(f"Uploading file: {f.name}, case_id={case_id}, content_type={content_type}")
            up = evidence.get_upload_url(case_id=case_id, file_name=f.name, content_type=content_type)

            # 2) Upload bytes to S3
            evidence.upload_to_presigned_url(up["upload_url"], content, content_type)

            # 3) Confirm upload to backend
            evidence.confirm_upload(up["evidence_id"], file_hash, len(content))

            # Store evidence_id into session
            st.session_state["evidence_ids"].append(up["evidence_id"])

        st.success(f"Uploaded and confirmed {len(uploaded_files)} evidence files.")
        st.write("Evidence IDs:", st.session_state["evidence_ids"])
