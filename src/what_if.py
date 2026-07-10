from copy import deepcopy

from src.predict import predict_loan


def suggest_improvements(user_data):

    suggestions = []

    # -----------------------------
    # Try Increasing Credit Score
    # -----------------------------
    temp = deepcopy(user_data)

    for score in range(
        int(user_data["Credit_Score"]),
        851,
        10
    ):

        temp["Credit_Score"] = score

        result, confidence = predict_loan(temp)

        if result == "Approved":

            suggestions.append({
    "title": "Increase Credit Score",
    "body": f"Increase the applicant's credit score to approximately {score} to improve loan eligibility."
})

            break

    # -----------------------------
    # Try Reducing Loan Amount
    # -----------------------------
    temp = deepcopy(user_data)

    loan = user_data["Loan_Amount"]

    while loan > 50000:

        loan -= 25000

        temp["Loan_Amount"] = loan

        result, confidence = predict_loan(temp)

        if result == "Approved":

            suggestions.append({
    "title": "Reduce Loan Amount",
    "body": f"Reduce the loan amount to approximately ₹{loan:,.0f} to improve loan eligibility."
})

            break

    # -----------------------------
    # Try Increasing Savings
    # -----------------------------
    temp = deepcopy(user_data)

    savings = user_data["Savings"]

    while savings < 1000000:

        savings += 50000

        temp["Savings"] = savings

        result, confidence = predict_loan(temp)

        if result == "Approved":

            suggestions.append({
    "title": "Increase Savings",
    "body": f"Increase the applicant's savings to approximately ₹{savings:,.0f} to improve loan eligibility."
})

            break

    # -----------------------------
    # Try Reducing DTI Ratio
    # -----------------------------
    temp = deepcopy(user_data)

    dti = user_data["DTI_Ratio"]

    while dti > 0.10:

        dti -= 0.02

        temp["DTI_Ratio"] = round(dti, 2)

        result, confidence = predict_loan(temp)

        if result == "Approved":

            suggestions.append({
    "title": "Reduce DTI Ratio",
    "body": f"Reduce the applicant's DTI ratio to around {round(dti,2)} to improve loan eligibility."
})

            break

    return suggestions