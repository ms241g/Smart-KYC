import streamlit as st
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import date
import uuid


# ----------------------------
# Domain Models
# ----------------------------
@dataclass(frozen=True)
class KYCCategory:
    id: str
    title: str
    description: str
    required_documents: List[str]
    required_fields: List[str]


# ----------------------------
# Citi-aligned KYC Categories
# ----------------------------
def load_kyc_categories() -> List[KYCCategory]:
    """
    In production: categories should be policy-driven from KYC policy service.
    """
    return [
        KYCCategory(
            id="cip",
            title="CIP (Customer Identification Program)",
            description="Identity verification for individual customers as per Citi KYC/CIP controls.",
            required_documents=[
                "Government-issued Photo ID (Passport / Driver's License / National ID)",
                "Secondary ID (if required by risk tier or discrepancy)"
            ],
            required_fields=["full_name", "dob", "citizenship", "address", "document_type"],
        ),
        KYCCategory(
            id="address_verification",
            title="Address Verification",
            description="Proof of residential address verification.",
            required_documents=[
                "Utility Bill (latest 3 months)",
                "Bank Statement (latest 3 months)",
                "Registered Rental Agreement (if applicable)"
            ],
            required_fields=["full_name", "dob", "citizenship", "address", "document_type"],
        ),
        KYCCategory(
            id="kyb",
            title="KYB (Know Your Business)",
            description="Business onboarding verification for legal entity and ownership.",
            required_documents=[
                "Certificate of Incorporation / Business Registration",
                "DBA / Trade Name Proof (if applicable)",
                "Tax Registration Certificate"
            ],
            required_fields=["business_name", "registration_id", "country_of_registration", "address"],
        ),
        KYCCategory(
            id="periodic_refresh",
            title="Periodic KYC Refresh",
            description="Periodic re-verification triggered due to regulatory refresh cycles.",
            required_documents=[
                "Valid Government ID",
                "Updated Proof of Address (latest 3 months)"
            ],
            required_fields=["full_name", "dob", "citizenship", "address", "document_type"],
        ),
        KYCCategory(
            id="edd",
            title="EDD (Enhanced Due Diligence)",
            description="Enhanced verification for high-risk customers / jurisdictions.",
            required_documents=[
                "Government ID",
                "Proof of Address",
                "Source of Funds / Wealth Declaration",
                "Additional supporting evidence (as required)"
            ],
            required_fields=["full_name", "dob", "citizenship", "address", "document_type", "source_of_funds"],
        ),
    ]


# ----------------------------
# UI Helpers
# ----------------------------
def render_header():
    st.set_page_config(
        page_title="Citi KYC Initiation Portal",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .main-title {
            font-size: 36px;
            font-weight: 800;
            color: #0B1F41;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 15px;
            color: #3D4B63;
            margin-top: 0px;
        }
        .section-title {
            font-size: 20px;
            font-weight: 700;
            color: #0B1F41;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="main-title">🏦 Citi KYC Initiation Portal</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Initiate KYC cases aligned to Citi compliance controls. All submissions are validated using AI-driven policy workflows.</div>',
        unsafe_allow_html=True
    )
    st.divider()


def render_sidebar(categories: List[KYCCategory]) -> KYCCategory:
    st.sidebar.header("KYC Case Categories (Citi)")

    category_map = {c.title: c for c in categories}
    selected = st.sidebar.radio(
        "Select KYC category",
        options=list(category_map.keys()),
        index=0,
    )

    st.sidebar.divider()
    st.sidebar.markdown("### Compliance Notice")
    st.sidebar.info(
        "All information submitted is processed under Citi KYC policy controls. "
        "AI-driven checks assist validation and discrepancy handling; final outcomes may require human approval."
    )

    return category_map[selected]


def render_required_docs(category: KYCCategory):
    st.markdown('<div class="section-title">📄 Required Evidence</div>', unsafe_allow_html=True)
    st.write(f"**Category:** {category.title}")
    st.caption(category.description)

    for doc in category.required_documents:
        st.write(f"✅ {doc}")


# ----------------------------
# Form Components
# ----------------------------
def render_customer_form(category: KYCCategory) -> Dict[str, Any]:
    st.markdown('<div class="section-title">🧾 Customer / Entity Information</div>', unsafe_allow_html=True)

    with st.form(key=f"kyc_form_{category.id}", clear_on_submit=False):

        # ---- Individual (CIP) fields
        full_name = st.text_input("Full Name *", placeholder="As per ID document")
        dob = st.date_input("Date of Birth *", min_value=date(1900, 1, 1), max_value=date.today())

        citizenship = st.selectbox(
            "Citizenship *",
            options=["India", "USA", "UK", "UAE", "Singapore", "Other"],
            index=0
        )

        document_type = st.selectbox(
            "Primary Document Type Submitted *",
            options=[
                "Passport",
                "Driver's License",
                "National ID",
                "Utility Bill",
                "Bank Statement",
                "Company Registration",
                "Other"
            ],
            index=0,
        )

        # ---- Address block
        st.markdown("### 🏠 Address Details")
        col1, col2 = st.columns(2)

        with col1:
            address_line1 = st.text_input("Address Line 1 *", placeholder="Street / Building")
            city = st.text_input("City *")
            state = st.text_input("State / Province")

        with col2:
            address_line2 = st.text_input("Address Line 2")
            postal_code = st.text_input("Postal Code *")
            country = st.text_input("Country *", value="India")

        # ---- Additional EDD details
        source_of_funds = ""
        if "source_of_funds" in category.required_fields:
            st.markdown("### 💰 Enhanced Due Diligence Details")
            source_of_funds = st.text_area(
                "Source of Funds / Source of Wealth *",
                placeholder="Provide details for compliance evaluation (salary, business income, investment, inheritance, etc.)",
            )

        # ---- Upload section
        st.markdown('<div class="section-title">📎 Upload Supporting Documents</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Accepted formats: PDF, JPG/PNG, DOC/DOCX",
            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
            accept_multiple_files=True,
        )

        # ---- Consent
        st.checkbox(
            "I confirm the submitted information is accurate and authorized for compliance review.",
            value=False,
            key="consent"
        )

        submitted = st.form_submit_button("Submit KYC Case ✅")

        payload = {
            "case_id": str(uuid.uuid4()),
            "category_id": category.id,
            "category_title": category.title,
            "customer_details": {
                "full_name": full_name.strip(),
                "dob": dob.isoformat() if dob else None,
                "citizenship": citizenship,
                "document_type": document_type,
                "address": {
                    "line1": address_line1.strip(),
                    "line2": address_line2.strip(),
                    "city": city.strip(),
                    "state": state.strip(),
                    "postal_code": postal_code.strip(),
                    "country": country.strip(),
                },
                "source_of_funds": source_of_funds.strip() if source_of_funds else None,
            },
            "upload_count": len(uploaded_files) if uploaded_files else 0,
        }

        return {
            "submitted": submitted,
            "payload": payload,
            "files": uploaded_files,
        }


# ----------------------------
# Backend Integration Placeholder
# ----------------------------
def call_ai_validation_backend(payload: Dict[str, Any], files) -> Dict[str, Any]:
    """
    In production:
      POST /v1/kyc/cases/initiate
        - payload JSON
        - files multipart upload
    """
    return {
        "status": "received",
        "message": "Case submitted to Citi AI KYC validation workflow.",
        "case_id": payload["case_id"],
        "workflow": [
            "Policy-aware document validation",
            "OCR + translation (if applicable)",
            "Discrepancy checks vs customer profile",
            "Resolution guidance and evidence collection",
            "Decision: Pass / Fail / Escalate to Compliance Review"
        ],
    }


# ----------------------------
# Main App
# ----------------------------
def main():
    render_header()
    categories = load_kyc_categories()
    category = render_sidebar(categories)

    st.markdown("## 🏁 Initiate a KYC Case")
    st.write(f"**Selected category:** {category.title}")
    st.caption(category.description)
    st.divider()

    render_required_docs(category)
    st.divider()

    result = render_customer_form(category)

    if result["submitted"]:
        payload = result["payload"]

        # Consent check
        if not st.session_state.get("consent"):
            st.error("Consent is required before submission.")
            return

        missing = []
        if not payload["customer_details"]["full_name"]:
            missing.append("Full Name")
        if not payload["customer_details"]["address"]["line1"]:
            missing.append("Address Line 1")
        if not payload["customer_details"]["address"]["city"]:
            missing.append("City")
        if not payload["customer_details"]["address"]["postal_code"]:
            missing.append("Postal Code")
        if payload["upload_count"] == 0:
            missing.append("At least one document upload")

        if missing:
            st.error(f"Please provide: {', '.join(missing)}")
            return

        with st.spinner("Submitting case and initiating AI validation workflow..."):
            response = call_ai_validation_backend(payload, result["files"])

        st.success(response["message"])
        st.info(f"**Case ID:** {response['case_id']}")

        st.markdown("### 🔄 Workflow Triggered")
        for step in response["workflow"]:
            st.write(f"➡️ {step}")

        with st.expander("View submitted payload (debug)"):
            st.json(payload)


if __name__ == "__main__":
    main()
