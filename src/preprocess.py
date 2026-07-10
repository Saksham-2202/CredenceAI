import pandas as pd
import joblib
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


# ----------------------------
# Load Dataset
# ----------------------------
def load_data(filepath):
    return pd.read_csv(filepath)


# ----------------------------
# Handle Missing Values
# ----------------------------
def handle_missing_values(df):

    categorical_columns = df.select_dtypes(include=["object"]).columns
    numerical_columns = df.select_dtypes(include=["number"]).columns

    num_imputer = SimpleImputer(strategy="mean")
    df[numerical_columns] = num_imputer.fit_transform(df[numerical_columns])

    cat_imputer = SimpleImputer(strategy="most_frequent")
    df[categorical_columns] = cat_imputer.fit_transform(df[categorical_columns])

    return df


# ----------------------------
# Encode Categorical Data
# ----------------------------
def encode_data(df):

    # Drop Applicant ID
    df = df.drop("Applicant_ID", axis=1)

    # Label Encoding
    education_encoder = LabelEncoder()
    loan_encoder = LabelEncoder()

    df["Education_Level"] = education_encoder.fit_transform(df["Education_Level"])
    df["Loan_Approved"] = loan_encoder.fit_transform(df["Loan_Approved"])

    # One Hot Encoding
    cols = [
        "Gender",
        "Marital_Status",
        "Loan_Purpose",
        "Property_Area",
        "Employment_Status",
        "Employer_Category"
    ]

    ohe = OneHotEncoder(
        drop="first",
        sparse_output=False,
        handle_unknown="ignore"
    )

    encoded_data = ohe.fit_transform(df[cols])

    encoded_df = pd.DataFrame(
        encoded_data,
        columns=ohe.get_feature_names_out(cols),
        index=df.index
    )

    df = pd.concat(
        [df.drop(columns=cols), encoded_df],
        axis=1
    )

    # Save Encoders
    joblib.dump(education_encoder, "models/education_encoder.pkl")
    joblib.dump(loan_encoder, "models/loan_encoder.pkl")
    joblib.dump(ohe, "models/onehot_encoder.pkl")

    return df


# ----------------------------
# Feature Engineering
# ----------------------------
def feature_engineering(df):

    df["DTI_Ratio_sq"] = df["DTI_Ratio"] ** 2
    df["Credit_score_sq"] = df["Credit_Score"] ** 2

    return df


# ----------------------------
# Complete Preprocessing
# ----------------------------
def preprocess_data(filepath):

    df = load_data(filepath)

    df = handle_missing_values(df)

    df = encode_data(df)

    df = feature_engineering(df)

    return df