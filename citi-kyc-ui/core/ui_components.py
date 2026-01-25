import streamlit as st

def render_header():
    st.set_page_config(page_title="Citi KYC Initiation Portal", page_icon="🏦", layout="wide")
    st.title("🏦 Citi KYC Initiation Portal")
    st.caption("Policy-driven KYC initiation and evidence submission. AI validation runs asynchronously under compliance controls.")
    st.divider()

def render_compliance_notice():
    st.info(
        "Compliance Notice: Submitted information is processed under Citi KYC controls. "
        "AI assists validation; outcomes may require compliance review."
    )

def show_discrepancies(discrepancies: list):
    if not discrepancies:
        st.success("No discrepancies found.")
        return
    st.warning("Action Required: discrepancies detected.")
    for d in discrepancies:
        with st.expander(f"{d['severity']} — {d['field']}"):
            st.write(d["message"])
            st.write(f"**Expected:** {d.get('expected_value')}")
            st.write(f"**Received:** {d.get('received_value')}")
            st.write(f"**Resolution:** {d.get('resolution_required')}")
