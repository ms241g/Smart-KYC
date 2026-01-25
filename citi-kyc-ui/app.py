import streamlit as st
from core.session import init_session
from core.ui_components import render_header

from pages import home, initiate_case, upload_evidence, case_tracker

def main():
    init_session()
    render_header()

    page = st.sidebar.selectbox(
        "Navigation",
        ["Home", "Initiate Case", "Upload Evidence", "Submit & Track"],
        index=0,
    )

    if page == "Home":
        home.render()
    elif page == "Initiate Case":
        initiate_case.render()
    elif page == "Upload Evidence":
        upload_evidence.render()
    else:
        case_tracker.render()

if __name__ == "__main__":
    main()
