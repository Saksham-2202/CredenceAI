import os
import streamlit as st

from src.ui import load_css, page_header, footer
from src.forms import build_applicant_form
from src.dashboard import (
    show_prediction,
    show_applicant_summary,
    explain_prediction
)

from src.predict import predict_loan
from src.what_if import suggest_improvements
#from src.pdf_report import generate_pdf

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Credence AI",
    page_icon="🏦",
    layout="wide",
)

# ----------------------------
# Session State Defaults
# ----------------------------
# BUG FIX: previously "prediction_done" was the only key initialized,
# but "result" / "confidence" / "user_data" were read later in the
# script before a prediction ever ran, causing an AttributeError on
# every fresh session. All keys are now initialized up front.
_defaults = {
    "prediction_done": False,
    "result": None,
    "confidence": None,
    "user_data": None,
    "report_generated": False,
}
for _key, _value in _defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value

load_css()

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:

    st.image("assets/logo.png", width=120)

    st.markdown("<div class='sidebar-brand'>🏦 Credence AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-caption'>Machine Learning Loan Approval System</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-label'>MODEL</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-model-badge'>● Naive Bayes</div>", unsafe_allow_html=True)

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            "<div class='sidebar-stat'>"
            "<div class='sidebar-stat-label'>Accuracy</div>"
            "<div class='sidebar-stat-value'>86%</div>"
            "</div>",
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            "<div class='sidebar-stat'>"
            "<div class='sidebar-stat-label'>Precision</div>"
            "<div class='sidebar-stat-value'>81%</div>"
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<div class='sidebar-stat' style='margin-top:8px;'>"
        "<div class='sidebar-stat-label'>Dataset</div>"
        "<div class='sidebar-stat-value'>1000 Records</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='sidebar-section-label' style='margin-top:20px;'>TECH STACK</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='sidebar-tags'>
            <span class='sidebar-tag'>Python</span>
            <span class='sidebar-tag'>Scikit-Learn</span>
            <span class='sidebar-tag'>Pandas</span>
            <span class='sidebar-tag'>Streamlit</span>
            <span class='sidebar-tag'>Joblib</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='sidebar-version'>Version 1.0</div>", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
# BUG FIX: page_header() was previously imported from src.ui but then
# shadowed by a duplicate local definition further down in this file
# that was never called - so the hero banner never rendered. The local
# duplicate has been removed; this now calls the real one from ui.py.
page_header()

# ----------------------------
# Build Form
# ----------------------------
predict, user_data = build_applicant_form()

# ----------------------------
# Predict Button
# ----------------------------
if predict:

    with st.spinner("Analyzing Applicant..."):
        result, confidence = predict_loan(user_data)

    st.session_state.prediction_done = True
    st.session_state.result = result
    st.session_state.confidence = confidence
    st.session_state.user_data = user_data

    # BUG FIX: report_generated used to stay True forever once set, so
    # re-running a prediction with different inputs would still hand
    # back the PDF from the very first prediction. Resetting it here
    # forces a fresh PDF for the new result.
    st.session_state.report_generated = False

# ----------------------------
# Show Results
# ----------------------------
suggestions = []

if st.session_state.prediction_done:

    show_applicant_summary(st.session_state.user_data)

    show_prediction(
        st.session_state.result,
        st.session_state.confidence
    )

    # -----------------------------
    # AI What-If Analysis
    # -----------------------------
    if st.session_state.result == "Rejected":

        st.markdown("<div class='section-heading'>💡 AI What-If Analysis</div>", unsafe_allow_html=True)

        suggestions = suggest_improvements(
            st.session_state.user_data
        )

        if suggestions:

            st.markdown(
                "<div class='whatif-intro'>The model found these changes that may improve approval:</div>",
                unsafe_allow_html=True
            )

            for suggestion in suggestions:

                st.markdown(
                    f"""
                    <div class="whatif-card">
                        <div class="whatif-title">✅ {suggestion['title']}</div>
                        <div class="whatif-body">{suggestion['body']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.markdown(
                "<div class='whatif-empty'>No simple improvement was found. "
                "Multiple financial factors may need to change together.</div>",
                unsafe_allow_html=True
            )

        explain_prediction(
            st.session_state.user_data,
            st.session_state.result
        )

    # # -----------------------------
    # # One-Click Download PDF Report
    # # -----------------------------
    # # BUG FIX: this block used to run unconditionally on every script
    # # execution, including before any prediction existed, which would
    # # crash the app immediately on first load. It is now correctly
    # # scoped inside "if st.session_state.prediction_done:".
    # if not st.session_state.report_generated:

    #     generate_pdf(
    #         user_data=st.session_state.user_data,
    #         result=st.session_state.result,
    #         confidence=st.session_state.confidence,
    #         suggestions=suggestions if st.session_state.result == "Rejected" else [],
    #         output_path="CredenceAI_Report.pdf",
    #         logo_path="assets/logo.png"
    #         )

    #     st.session_state.report_generated = True

    # if os.path.exists("CredenceAI_Report.pdf"):

    #     st.markdown("<div class='section-heading'>📄 Loan Assessment Report</div>", unsafe_allow_html=True)

    #     with open("CredenceAI_Report.pdf", "rb") as pdf_file:

    #         st.download_button(
    #             "📄 Download Loan Assessment Report",
    #             data=pdf_file.read(),
    #             file_name="CredenceAI_Report.pdf",
    #             mime="application/pdf",
    #             use_container_width=True,
    #             type="primary"
    #         )

# ----------------------------
# Footer
# ----------------------------
footer()