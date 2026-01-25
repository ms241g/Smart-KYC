import streamlit as st
from api import cases
from core.ui_components import render_compliance_notice

def render():
    st.subheader("🧾 Initiate Case")
    render_compliance_notice()

    if not st.session_state.get("selected_category"):
        st.warning("Select a category on Home first.")
        return

    customer_id = st.text_input("Customer ID *", value=st.session_state.get("customer_id", ""))
    st.session_state["customer_id"] = customer_id

    category = st.session_state["selected_category"]
    st.write(f"**Selected Category:** {category['title']}")

    if st.button("Initiate Case ✅", disabled=not customer_id.strip()):
        resp = cases.initiate_case(customer_id=customer_id.strip(), category_id=category["id"])
        st.session_state["case_id"] = resp["case_id"]
        st.success(f"Case initiated. Internal Case ID: {resp['case_id']}")
