import streamlit as st


# ----------------------------------------
# Applicant Form
# ----------------------------------------
def build_applicant_form():
    """
    Renders the applicant + financial + loan detail inputs.

    IMPORTANT: the keys, types, default values, and min/max bounds of
    every field below are unchanged from the original implementation.
    Only the visual grouping (cards, headings, icons) was redesigned.
    Downstream code (predict.py, preprocess.py) depends on these exact
    dict keys, so do not rename them.
    """

    # ---------------- Applicant Information ----------------
    with st.container(border=True):

        st.markdown(
            "<div class='section-title'>👤 Applicant Information</div>"
            "<div class='section-subtext'>Personal and employment details</div>",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            gender = st.selectbox(
                "Gender",
                ["Male", "Female"]
            )

            age = st.number_input(
                "Age",
                min_value=18,
                max_value=80,
                value=30
            )

        with col2:
            marital_status = st.selectbox(
                "Marital Status",
                ["Single", "Married"]
            )

            dependents = st.number_input(
                "Dependents",
                min_value=0,
                max_value=10,
                value=0
            )

        with col3:
            education = st.selectbox(
                "Education Level",
                [
                    "Graduate",
                    "Postgraduate",
                    "Undergraduate"
                ]
            )

            employment = st.selectbox(
                "Employment Status",
                [
                    "Salaried",
                    "Self-employed",
                    "Business"
                ]
            )

        employer_category = st.selectbox(
            "Employer Category",
            [
                "Government",
                "Private",
                "MNC",
                "Unemployed"
            ]
        )

    # ---------------- Financial Information ----------------
    with st.container(border=True):

        st.markdown(
            "<div class='section-title'>💰 Financial Information</div>"
            "<div class='section-subtext'>Income, credit and liability details</div>",
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            applicant_income = st.number_input(
                "Applicant Income",
                min_value=0.0,
                value=30000.0
            )

            credit_score = st.number_input(
                "Credit Score",
                min_value=300,
                max_value=900,
                value=700
            )

            savings = st.number_input(
                "Savings",
                min_value=0.0,
                value=50000.0
            )

        with c2:

            coapplicant_income = st.number_input(
                "Coapplicant Income",
                min_value=0.0,
                value=0.0
            )

            existing_loans = st.number_input(
                "Existing Loans",
                min_value=0,
                max_value=10,
                value=0
            )

            collateral_value = st.number_input(
                "Collateral Value",
                min_value=0.0,
                value=100000.0
            )

        with c3:

            dti_ratio = st.number_input(
                "DTI Ratio",
                min_value=0.0,
                max_value=1.0,
                value=0.30,
                step=0.01
            )

            loan_amount = st.number_input(
                "Loan Amount",
                min_value=1000.0,
                value=100000.0
            )

            loan_term = st.number_input(
                "Loan Term (Months)",
                min_value=6,
                max_value=360,
                value=60
            )

    # ---------------- Loan Details ----------------
    with st.container(border=True):

        st.markdown(
            "<div class='section-title'>🏦 Loan Details</div>"
            "<div class='section-subtext'>Purpose and property information</div>",
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:

            loan_purpose = st.selectbox(
                "Loan Purpose",
                [
                    "Home",
                    "Education",
                    "Personal",
                    "Car"
                ]
            )

        with c2:

            property_area = st.selectbox(
                "Property Area",
                [
                    "Urban",
                    "Semiurban",
                    "Rural"
                ]
            )

    predict = st.button(
        "🔍 Predict Loan Eligibility",
        use_container_width=True
    )

    user_data = {
        "Gender": gender,
        "Marital_Status": marital_status,
        "Education_Level": education,
        "Employment_Status": employment,
        "Employer_Category": employer_category,
        "Age": age,
        "Dependents": dependents,
        "Applicant_Income": applicant_income,
        "Coapplicant_Income": coapplicant_income,
        "Credit_Score": credit_score,
        "Existing_Loans": existing_loans,
        "Savings": savings,
        "Collateral_Value": collateral_value,
        "DTI_Ratio": dti_ratio,
        "Loan_Amount": loan_amount,
        "Loan_Term": loan_term,
        "Loan_Purpose": loan_purpose,
        "Property_Area": property_area,
    }

    return predict, user_data