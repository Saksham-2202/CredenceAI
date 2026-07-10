import streamlit as st

from pathlib import Path


# ----------------------------
# Load CSS
# ----------------------------
def load_css():
    """
    Loads assets/style.css and injects it into the page.
    Silently no-ops (with a small warning) if the file is missing,
    instead of crashing the whole app.
    """

    css_path = Path(__file__).parent.parent / "assets" / "style.css"

    if not css_path.exists():
        st.warning("Stylesheet not found at assets/style.css - using default Streamlit styling.")
        return

    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


# ----------------------------
# Header
# ----------------------------
def page_header():
    """
    Renders the navy hero banner at the top of the app.
    Bug fix: this used to be imported but shadowed by a duplicate
    local definition in app.py, so it never actually rendered.
    """

    st.markdown(
        """
        <div class="hero-banner">
            <div class="main-title">🏦 Credence AI</div>
            <div class="sub-title">AI Powered Loan Eligibility Assessment</div>
            <div class="hero-description">
                Intelligent, explainable loan eligibility prediction powered by
                Machine Learning. Enter applicant details below to generate an
                instant decision with a full AI-generated assessment report.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# Footer
# ----------------------------
def footer():
    """
    Renders the bottom footer.
    Bug fix: same shadowing issue as page_header() - this now actually
    gets called from app.py.
    """

    st.markdown(
        """
        <div class="footer">
            © 2026 Credence AI &nbsp;•&nbsp; Developed with Python, Scikit-Learn &amp; Streamlit
            &nbsp;•&nbsp; No physical signature required
        </div>
        """,
        unsafe_allow_html=True,
    )