import uuid
import streamlit as st

def init_session():
    defaults = {
        "customer_id": "",
        "selected_category": None,
        "requirements": None,
        "case_id": None,
        "evidence_ids": [],
        "idempotency_key": str(uuid.uuid4()),
        "latest_status": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_case_session():
    st.session_state["selected_category"] = None
    st.session_state["requirements"] = None
    st.session_state["case_id"] = None
    st.session_state["evidence_ids"] = []
    st.session_state["idempotency_key"] = str(uuid.uuid4())
    st.session_state["latest_status"] = None
