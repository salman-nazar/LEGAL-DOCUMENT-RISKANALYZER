"""
app.py
Streamlit front-end for the Document AI Risk Analyzer.

Flow:
Login/Register -> Upload Contract -> Extract Text -> Analyze Clauses ->
Detect Risks -> Generate Summary -> Dashboard -> Export PDF Report
"""

import os
import streamlit as st

import database
import auth
import analyzer
import report_generator

UPLOAD_DIR = "uploads"
REPORT_DIR = "reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

st.set_page_config(page_title="Document AI Risk Analyzer", page_icon="📄", layout="wide")

database.init_db()

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "selected_doc_id" not in st.session_state:
    st.session_state.selected_doc_id = None


def logout():
    st.session_state.user = None
    st.session_state.selected_doc_id = None


# ---------------------------------------------------------------------------
# AUTH SCREENS
# ---------------------------------------------------------------------------
def show_login_register():
    st.title("📄 Document AI Risk Analyzer")
    st.caption("Offline contract analysis — login or create an account to continue.")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                success, message, user = auth.login_user(username, password)
                if success:
                    st.session_state.user = user
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                success, message = auth.register_user(
                    new_username, new_email, new_password, confirm_password
                )
                if success:
                    st.success(message + " Please log in from the Login tab.")
                else:
                    st.error(message)


# ---------------------------------------------------------------------------
# UPLOAD + ANALYSIS
# ---------------------------------------------------------------------------
def process_uploaded_file(uploaded_file, user_id):
    save_path = os.path.join(UPLOAD_DIR, f"{user_id}_{uploaded_file.name}")
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Extracting text and running risk analysis..."):
        result = analyzer.analyze_document(save_path)
        doc_id = database.save_document(user_id, uploaded_file.name, save_path)
        database.save_analysis(
            doc_id, result["clauses"], result["risks"],
            result["summary"], result["risk_score"]
        )

    st.session_state.selected_doc_id = doc_id
    st.success(f"'{uploaded_file.name}' analyzed successfully.")
    st.rerun()


def show_upload_page():
    st.header("Upload Contract")
    st.write("Supported formats: PDF, DOCX, TXT")

    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        if st.button("Analyze Document", type="primary"):
            try:
                process_uploaded_file(uploaded_file, st.session_state.user["id"])
            except Exception as e:
                st.error(f"Analysis failed: {e}")


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
def risk_badge(score):
    if score is None:
        return "—"
    if score >= 60:
        return f"🔴 High ({score})"
    if score >= 30:
        return f"🟠 Medium ({score})"
    return f"🟢 Low ({score})"


def show_dashboard():
    st.header("Dashboard")
    user_id = st.session_state.user["id"]
    docs = database.get_all_documents_with_scores(user_id)

    if not docs:
        st.info("No documents uploaded yet. Use the Upload page to get started.")
        return

    for d in docs:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 2])
            col1.markdown(f"**{d['filename']}**")
            col1.caption(f"Uploaded: {d['uploaded_at'][:19].replace('T', ' ')}")
            col2.markdown(risk_badge(d["risk_score"]))
            if col3.button("View Analysis", key=f"view_{d['id']}"):
                st.session_state.selected_doc_id = d["id"]
                st.rerun()


# ---------------------------------------------------------------------------
# ANALYSIS DETAIL + REPORT EXPORT
# ---------------------------------------------------------------------------
def show_analysis_detail():
    doc_id = st.session_state.selected_doc_id
    doc = database.get_document_by_id(doc_id)
    analysis = database.get_analysis_by_document(doc_id)

    if not doc or not analysis:
        st.error("Analysis not found.")
        return

    if st.button("← Back to Dashboard"):
        st.session_state.selected_doc_id = None
        st.rerun()

    st.header(f"Analysis: {doc['filename']}")

    clauses = analysis["clauses"]
    risks = analysis["risks"]
    summary = analysis["summary"]
    score = analysis["risk_score"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Contract Type", clauses["contract_type"])
    col2.metric("Risk Score", f"{score}/100", summary.get("risk_band", ""))
    col3.metric("Risks Found", len([r for r in risks if r["risk"] != "No Major Risks Detected"]))

    st.subheader("Executive Summary")
    st.write(summary["executive_summary"])

    st.subheader("Key Contract Fields")
    field_labels = {
        "contract_type": "Contract Type",
        "effective_date": "Effective Date",
        "expiry_date": "Expiry Date",
        "payment_terms": "Payment Terms",
        "confidentiality": "Confidentiality",
        "termination": "Termination",
        "renewal": "Renewal",
        "responsibilities": "Responsibilities",
    }
    for key, label in field_labels.items():
        st.markdown(f"**{label}:** {clauses.get(key, 'Not found')}")

    st.subheader("Detected Risks")
    for r in risks:
        icon = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(r["severity"], "⚪")
        with st.expander(f"{icon} {r['risk']} — {r['severity']} severity"):
            st.write(r["description"])

    st.subheader("Recommendations")
    for rec in summary["recommendations"]:
        st.markdown(f"- {rec}")

    st.divider()
    if st.button("📥 Generate PDF Report", type="primary"):
        report_path = os.path.join(REPORT_DIR, f"report_{doc_id}.pdf")
        report_generator.generate_pdf_report(doc["filename"], analysis, report_path)
        with open(report_path, "rb") as f:
            st.download_button(
                "Download Report",
                data=f.read(),
                file_name=f"RiskReport_{doc['filename']}.pdf",
                mime="application/pdf"
            )


# ---------------------------------------------------------------------------
# MAIN APP SHELL
# ---------------------------------------------------------------------------
def main():
    if st.session_state.user is None:
        show_login_register()
        return

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['username']}")
        page = st.radio("Navigate", ["Dashboard", "Upload Contract"])
        st.divider()
        if st.button("Logout"):
            logout()
            st.rerun()

    if st.session_state.selected_doc_id is not None:
        show_analysis_detail()
    elif page == "Upload Contract":
        show_upload_page()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()