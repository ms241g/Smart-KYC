import streamlit as st
from api import cases
import hashlib
from api import evidence

from core.ui_components import show_discrepancies, render_compliance_notice

def render_new_form_fields(required_fields: list) -> dict:
    """
    Dynamic form based on required_fields from policy.
    Values stored in session_state for persistence across reruns.
    """
    st.markdown("### Customer / Entity Details")

    def _get(key, default=""):
        return st.session_state.get(key, default)

    data = {}

    if "full_name" in required_fields:
        data["full_name"] = st.text_input("Full Name *", key="full_name", value=_get("full_name"))

    if "dob" in required_fields:
        data["dob"] = st.text_input("DOB (YYYY-MM-DD) *", key="dob", value=_get("dob"))

    if "citizenship" in required_fields:
        data["citizenship"] = st.text_input("Citizenship *", key="citizenship", value=_get("citizenship"))

    if "address" in required_fields:
        st.markdown("#### Address")
        data["address"] = {
            "line1": st.text_input("Address Line 1 *", key="addr_line1", value=_get("addr_line1")),
            "line2": st.text_input("Address Line 2", key="addr_line2", value=_get("addr_line2")),
            "city": st.text_input("City *", key="addr_city", value=_get("addr_city")),
            "state": st.text_input("State/Province", key="addr_state", value=_get("addr_state")),
            "postal_code": st.text_input("Postal Code *", key="addr_postal", value=_get("addr_postal")),
            "country": st.text_input("Country *", key="addr_country", value=_get("addr_country")),
        }

    if "business_name" in required_fields:
        data["business_name"] = st.text_input("Business Name *", key="business_name", value=_get("business_name"))

    if "registration_id" in required_fields:
        data["registration_id"] = st.text_input("Registration ID *", key="registration_id", value=_get("registration_id"))

    if "country_of_registration" in required_fields:
        data["country_of_registration"] = st.text_input("Country of Registration *", key="country_of_registration", value=_get("country_of_registration"))

    if "source_of_funds" in required_fields:
        data["source_of_funds"] = st.text_area("Source of Funds *", key="source_of_funds", value=_get("source_of_funds"))

    return data

def build_payload_from_session(required_fields):
    data = {}

    if "full_name" in required_fields:
        data["full_name"] = st.session_state.get("full_name")
    if "dob" in required_fields:
        data["dob"] = st.session_state.get("dob")
    if "citizenship" in required_fields:
        data["citizenship"] = st.session_state.get("citizenship")

    if "address" in required_fields:
        data["address"] = {
            "line1": st.session_state.get("addr_line1"),
            "line2": st.session_state.get("addr_line2"),
            "city": st.session_state.get("addr_city"),
            "state": st.session_state.get("addr_state"),
            "postal_code": st.session_state.get("addr_postal"),  # 🔥 FIXED
            "country": st.session_state.get("addr_country"),
        }

    if "business_name" in required_fields:
        data["business_name"] = st.session_state.get("business_name")

    if "registration_id" in required_fields:
        data["registration_id"] = st.session_state.get("registration_id")

    if "country_of_registration" in required_fields:
        data["country_of_registration"] = st.session_state.get("country_of_registration")

    if "source_of_funds" in required_fields:
        data["source_of_funds"] = st.session_state.get("source_of_funds")

    return data


def render():
    st.subheader("📌 Submit & Track Case")
    render_compliance_notice()

    case_id = st.session_state.get("case_id")
    if not case_id:
        st.warning("Initiate a case first.")
        return

    req = st.session_state.get("requirements") or {}
    required_fields = req.get("required_fields", [])
    evidence_ids = st.session_state.get("evidence_ids", [])

    st.markdown(f"**Internal Case ID:** `{case_id}`")
    st.markdown(f"**Evidence Uploaded:** {len(evidence_ids)}")

    st.divider()
    customer_details = render_new_form_fields(required_fields)

    consent = st.checkbox("I confirm submitted details are accurate and authorized for compliance review.", value=False)

    #submit_disabled = st.session_state.get("latest_status", {}).get("status") in ["VALIDATING", "ACTION_REQUIRED", "VALIDATED", "IN_REVIEW"]
    latest_status = st.session_state.get("latest_status") or {}
    submit_disabled = isinstance(latest_status, dict) and latest_status.get("status") in [
    "VALIDATING", "ACTION_REQUIRED", "VALIDATED", "IN_REVIEW"
    ]

    if st.button("Submit Case for Validation ✅", disabled=submit_disabled):
        if not consent:
            st.error("Consent required.")
            return
        if not evidence_ids:
            st.error("Upload at least one evidence document.")
            return

        resp = cases.submit_case(
            case_id=case_id,
            customer_details=customer_details,
            evidence_ids=evidence_ids,
            consent=True,
            idempotency_key=st.session_state["idempotency_key"],
        )
        st.success(f"Submitted case. Status: {resp['status']}")


    st.divider()

    if st.button("Refresh Status 🔄"):
        status = cases.case_status(case_id)
        st.session_state["latest_status"] = status

    status = st.session_state.get("latest_status")
    if status:
        st.markdown(f"### Current Status: `{status['status']}`")
        show_discrepancies(status.get("discrepancies", []))
        discrepancies = status.get("discrepancies", [])
        doc_type_issue = any(
            d.get("field") == "document_type" and d.get("resolution_required", True)
            for d in discrepancies
        )

        st.write("Next steps:", status.get("next_steps", []))

        if status["status"] == "ACTION_REQUIRED":
            st.warning("Resolve discrepancies then re-submit corrections.")

            if doc_type_issue:
                st.warning("The uploaded document type is not valid for this KYC category. Please upload a correct document.")

                replacement_file = st.file_uploader(
                    "Upload Replacement Document",
                    type=["pdf", "jpg", "jpeg", "png"],
                    accept_multiple_files=False,
                    key="replacement_doc"
                )

                if replacement_file:
                    with st.spinner("Uploading replacement document..."):
                        ext = replacement_file.name.split(".")[-1].lower()
                        content_type = {
                            "pdf": "application/pdf",
                            "jpg": "image/jpeg",
                            "jpeg": "image/jpeg",
                            "png": "image/png",
                        }.get(ext, "application/octet-stream")

                        content = replacement_file.getvalue()
                        file_hash = hashlib.sha256(content).hexdigest()

                        up = evidence.get_upload_url(
                            case_id=case_id,
                            file_name=replacement_file.name,
                            content_type=content_type
                        )

                        evidence.upload_to_presigned_url(up["upload_url"], content, content_type)
                        evidence.confirm_upload(up["evidence_id"], file_hash, len(content))

                        st.session_state.setdefault("evidence_ids", []).append(up["evidence_id"])
                        st.success("Replacement document uploaded successfully.")


            if st.button("Re-Validate (Resolve) 🔁"):
                updated_details = build_payload_from_session(required_fields)

                cases.resolve_case(
                    case_id=case_id,
                    updated_customer_details=updated_details,
                    additional_evidence_ids=st.session_state.get("evidence_ids", [])
                )

                st.success("Re-validation triggered. Refresh status in a moment.")


        discrepancies = status.get("discrepancies", [])
            
        actionable = [d for d in discrepancies if d.get("resolution_required", True)]

        can_escalate = (
            status["status"] == "VALIDATED" or
            (status["status"] == "ACTION_REQUIRED" and len(actionable) == 0)
        )

        if can_escalate:
            st.success("You can submit this case for human compliance review.")
            if status["status"] == "VALIDATED":
                st.info("Automated validation complete. Final step is human compliance review.")

            if st.button("Submit for Human Review 🧑‍⚖️"):
                resp = cases.submit_for_review(case_id)
                st.success(f"Submitted for review. Final Case ID: {resp['final_case_id']}")
                st.code(resp["final_case_id"])

