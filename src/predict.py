import joblib
import pandas as pd

# ----------------------------
# Load Saved Model and Encoders
# ----------------------------
model = joblib.load("models/model.pkl")
scaler = joblib.load("models/scaler.pkl")
feature_names = joblib.load("models/features.pkl")

education_encoder = joblib.load("models/education_encoder.pkl")
loan_encoder = joblib.load("models/loan_encoder.pkl")
onehot_encoder = joblib.load("models/onehot_encoder.pkl")


# ----------------------------
# Loan Prediction Function
# ----------------------------
def predict_loan(input_data):

    # Convert user input into DataFrame
    df = pd.DataFrame([input_data])

    # ----------------------------
    # Label Encoding
    # ----------------------------
    df["Education_Level"] = education_encoder.transform(
        df["Education_Level"]
    )

    # ----------------------------
    # One Hot Encoding
    # ----------------------------
    categorical_columns = [
        "Gender",
        "Marital_Status",
        "Loan_Purpose",
        "Property_Area",
        "Employment_Status",
        "Employer_Category"
    ]

    encoded = onehot_encoder.transform(df[categorical_columns])

    encoded_df = pd.DataFrame(
        encoded,
        columns=onehot_encoder.get_feature_names_out(categorical_columns),
        index=df.index
    )

    df = pd.concat(
        [df.drop(columns=categorical_columns), encoded_df],
        axis=1
    )

    # ----------------------------
    # Feature Engineering
    # ----------------------------
    df["DTI_Ratio_sq"] = df["DTI_Ratio"] ** 2
    df["Credit_score_sq"] = df["Credit_Score"] ** 2

    # ----------------------------
    # Prepare Features
    # ----------------------------
    X = df.drop(
        columns=[
            "Credit_Score",
            "DTI_Ratio"
        ]
    )

    # ----------------------------
    # Match Training Columns
    # ----------------------------

    # Add missing columns
    for col in feature_names:
        if col not in X.columns:
            X[col] = 0

    # Remove extra columns and reorder
    X = X[feature_names]

    # ----------------------------
    # Feature Scaling
    # ----------------------------
    X_scaled = scaler.transform(X)

    # ----------------------------
    # Prediction
    # ----------------------------
    prediction = model.predict(X_scaled)[0]

    confidence = model.predict_proba(X_scaled)[0].max()

    result = "Approved" if prediction == 1 else "Rejected"

    return result, confidence

