import joblib

from preprocess import preprocess_data

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

import pandas as pd

df = pd.read_csv("data/2 loan_approval_data.csv")

print(df["Loan_Approved"].value_counts())
print(df["Loan_Approved"].value_counts(normalize=True) * 100)

# ----------------------------
# Load and Prepare Data
# ----------------------------
def load_dataset():

    df = preprocess_data("data/2 loan_approval_data.csv")

    X = df.drop(
        columns=[
            "Loan_Approved",
            "Credit_Score",
            "DTI_Ratio"
        ]
    )

    y = df["Loan_Approved"]

    return X, y


# ----------------------------
# Split and Scale Data
# ----------------------------
def prepare_data(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


# ----------------------------
# Evaluate Model
# ----------------------------
def evaluate_model(model_name, model, X_test, y_test):

    y_pred = model.predict(X_test)

    print(f"\n========== {model_name} ==========")
    print("Accuracy :", accuracy_score(y_test, y_pred))
    print("Precision :", precision_score(y_test, y_pred))
    print("Recall :", recall_score(y_test, y_pred))
    print("F1 Score :", f1_score(y_test, y_pred))


# ----------------------------
# Train Logistic Regression
# ----------------------------
def train_logistic(X_train, y_train):

    model = LogisticRegression()
    model.fit(X_train, y_train)

    return model


# ----------------------------
# Train KNN
# ----------------------------
def train_knn(X_train, y_train):

    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)

    return model


# ----------------------------
# Train Naive Bayes
# ----------------------------
def train_naive_bayes(X_train, y_train):

    model = GaussianNB()
    model.fit(X_train, y_train)

    return model


# ----------------------------
# Save Best Model
# ----------------------------
def save_model(model, scaler, feature_names):

    joblib.dump(model, "models/model.pkl")
    joblib.dump(scaler, "models/scaler.pkl")

    # Save feature order
    joblib.dump(feature_names, "models/features.pkl")

    print("\n✅ Model Saved Successfully!")
    print("Saved Files:")
    print("✔ model.pkl")
    print("✔ scaler.pkl")
    print("✔ features.pkl")
    print("✔ education_encoder.pkl")
    print("✔ loan_encoder.pkl")
    print("✔ onehot_encoder.pkl")


# ----------------------------
# Main Function
# ----------------------------
def main():

    X, y = load_dataset()
    

    X_train, X_test, y_train, y_test, scaler = prepare_data(X, y)

    logistic_model = train_logistic(X_train, y_train)
    evaluate_model("Logistic Regression", logistic_model, X_test, y_test)

    knn_model = train_knn(X_train, y_train)
    evaluate_model("KNN", knn_model, X_test, y_test)

    nb_model = train_naive_bayes(X_train, y_train)
    evaluate_model("Naive Bayes", nb_model, X_test, y_test)

    # Save Best Model
    save_model(
        nb_model,
        scaler,
        X.columns.tolist()
    )


if __name__ == "__main__":
    main()