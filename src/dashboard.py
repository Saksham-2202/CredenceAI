import streamlit as st


# -----------------------------------
# Applicant Summary Card
# -----------------------------------
def show_applicant_summary(user_data):
    """
    Same signature and same user_data keys as before.
    Only the visual output was redesigned.
    """

    st.markdown(
        '<div class="summary-title">📋 Applicant Summary</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Credit Score</div>
            <div class="kpi-value">{int(user_data['Credit_Score'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Monthly Income</div>
            <div class="kpi-value">₹{user_data['Applicant_Income']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Loan Amount</div>
            <div class="kpi-value">₹{user_data['Loan_Amount']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">DTI Ratio</div>
            <div class="kpi-value">{user_data['DTI_Ratio']*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='detail-title'>👤 Applicant Details</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="detail-row"><span>Age:</span> {user_data['Age']} Years</div>
        <div class="detail-row"><span>Gender:</span> {user_data['Gender']}</div>
        <div class="detail-row"><span>Marital Status:</span> {user_data['Marital_Status']}</div>
        <div class="detail-row"><span>Education:</span> {user_data['Education_Level']}</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="detail-row"><span>Employment:</span> {user_data['Employment_Status']}</div>
        <div class="detail-row"><span>Employer Category:</span> {user_data['Employer_Category']}</div>
        <div class="detail-row"><span>Loan Purpose:</span> {user_data['Loan_Purpose']}</div>
        <div class="detail-row"><span>Property Area:</span> {user_data['Property_Area']}</div>
        """, unsafe_allow_html=True)


# -----------------------------------
# AI Decision Card
# -----------------------------------
def show_prediction(result, confidence):
    """
    Same signature as before: result is "Approved"/"Rejected",
    confidence is a 0-1 float. Only the visual output changed.
    """

    st.markdown("<div class='section-heading'>📊 AI Decision</div>", unsafe_allow_html=True)

    approved = result == "Approved"
    badge_class = "approved" if approved else "rejected"
    badge_text = "✅ Loan Approved" if approved else "❌ Loan Rejected"
    caption_text = (
        "The applicant satisfies the financial criteria required by the prediction model."
        if approved else
        "The applicant is considered high risk by the prediction model."
    )

    st.markdown(f"""
    <div class="decision-card">
        <div class="decision-header">
            <div>
                <div class="decision-badge {badge_class}">{badge_text}</div>
                <div class="decision-caption">{caption_text}</div>
            </div>
            <div class="confidence-block">
                <div class="confidence-label">CONFIDENCE</div>
                <div class="confidence-value {badge_class}">{confidence*100:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(confidence)

    if approved:
        st.markdown("""
        <div class="risk-card low">
        🟢 <strong>Risk Level: LOW</strong><br>
        Recommended for further manual verification. The applicant appears financially reliable.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="risk-card high">
        🔴 <strong>Risk Level: HIGH</strong><br>
        Manual review is recommended. Loan approval is not advised.
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------
# Explainable AI
# -----------------------------------
def explain_prediction(user_data, prediction):
    """
    Same signature and same underlying text content as before.
    Only the visual container changed from st.success/st.warning/etc.
    to a styled card.
    """

    approved = prediction == "Approved"
    card_class = "approved" if approved else "rejected"

    st.markdown("<div class='section-heading'>🧠 AI Explanation</div>", unsafe_allow_html=True)

    if approved:

        st.markdown(
            f'<div class="explain-card {card_class}">'
            f'<div class="explain-body">'
            f'The Machine Learning model classified this applicant as <strong>Low Risk</strong>. '
            f'The prediction was made after evaluating all applicant attributes together, '
            f'rather than relying on a single financial indicator.'
            f'</div>'
            f'<div class="explain-subheading">Profile Summary</div>'
            f'<div class="profile-line">✅ Credit Score: <strong>{user_data["Credit_Score"]}</strong></div>'
            f'<div class="profile-line">✅ Debt-to-Income Ratio: <strong>{user_data["DTI_Ratio"]}</strong></div>'
            f'<div class="profile-line">✅ Savings Balance: <strong>₹{user_data["Savings"]:,.0f}</strong></div>'
            f'<div class="profile-line">✅ Existing Loans: <strong>{user_data["Existing_Loans"]}</strong></div>'
            f'<div class="profile-line">✅ Loan Amount: <strong>₹{user_data["Loan_Amount"]:,.0f}</strong></div>'
            f'<div class="explain-subheading">Overall Assessment</div>'
            f'<div class="explain-body">'
            f'The applicant\'s overall financial profile is statistically similar to '
            f'previously approved loan applications in the training dataset. '
            f'The model found no major risk patterns requiring additional review.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="explain-card {card_class}">'
            f'<div class="explain-body">'
            f'The Machine Learning model classified this applicant as <strong>High Risk</strong>. '
            f'Although some financial indicators appear satisfactory, the overall combination '
            f'of applicant attributes is statistically closer to previously rejected loan applications.'
            f'</div>'
            f'<div class="explain-subheading">Profile Summary</div>'
            f'<div class="profile-line">• Credit Score: <strong>{user_data["Credit_Score"]}</strong></div>'
            f'<div class="profile-line">• Debt-to-Income Ratio: <strong>{user_data["DTI_Ratio"]}</strong></div>'
            f'<div class="profile-line">• Savings Balance: <strong>₹{user_data["Savings"]:,.0f}</strong></div>'
            f'<div class="profile-line">• Existing Loans: <strong>{user_data["Existing_Loans"]}</strong></div>'
            f'<div class="profile-line">• Loan Amount: <strong>₹{user_data["Loan_Amount"]:,.0f}</strong></div>'
            f'<div class="explain-subheading">Overall Assessment</div>'
            f'<div class="explain-body">'
            f'This prediction is based on the combined influence of all applicant features '
            f'learned from historical loan records. The rejection does <strong>not</strong> '
            f'necessarily mean a single factor is poor. Instead, the complete applicant '
            f'profile resembles previous rejected applications in the training data.'
            f'<br><br>'
            f'<strong>Manual verification is recommended before making the final lending decision.</strong>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )