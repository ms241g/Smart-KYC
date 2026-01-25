import streamlit as st
from api import policies
from core.session import reset_case_session
from core.ui_components import render_compliance_notice
from core.config import DEFAULT_COUNTRY, DEFAULT_RISK_TIER

def render():
    st.subheader("🏁 Start New KYC Case")
    render_compliance_notice()

    if st.button("Start New Case"):
        reset_case_session()
        st.success("New session started. Select a category below.")

    cat_resp = policies.list_categories()
    categories = cat_resp.get("categories", [])

    if not categories:
        st.error("No KYC categories found.")
        return

    options = {c["title"]: c for c in categories}
    selected_title = st.radio("Select KYC category", list(options.keys()))
    selected = options[selected_title]

    # Fetch requirements on selection
    req = policies.get_requirements(selected["id"], DEFAULT_COUNTRY, DEFAULT_RISK_TIER)

    st.session_state["selected_category"] = selected
    st.session_state["requirements"] = req

    st.markdown("### 📄 Category Requirements (Policy Driven)")
    st.write(f"**Category:** {selected['title']}")
    st.caption(selected["description"])

    st.markdown("**Required Fields**")
    st.write(req.get("required_fields", []))

    st.markdown("**Allowed Document Types**")
    st.write(req.get("required_documents", []))

    st.markdown("**Policy Version**")
    st.code(req.get("policy_version", "unknown"))
