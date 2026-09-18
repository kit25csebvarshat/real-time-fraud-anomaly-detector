import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score, accuracy_score
from app.ml.dataset_generator import generate_synthetic_dataset

FEATURE_COLUMNS = [
    "permission_count",
    "sensitive_permission_count",
    "email_read",
    "email_send",
    "file_read",
    "file_write",
    "calendar_read",
    "calendar_write",
    "contacts_read",
    "contacts_write",
    "admin_access",
    "developer_verified",
    "developer_age",
    "application_age",
    "user_count",
    "purpose_permission_mismatch",
    "suspicious_permission_combination"
]

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "random_forest_model.joblib")

def train_and_evaluate_model():
    print("Generating synthetic OAuth risk dataset...")
    df = generate_synthetic_dataset(num_samples=2000)
    
    X = df[FEATURE_COLUMNS]
    y = df["risk_level"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Training Random Forest Classifier on {len(X_train)} samples...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted")
    rec = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")
    cm = confusion_matrix(y_test, y_pred)

    print("\n--- ML Model Evaluation Metrics ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1 Score:  {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["LOW", "MEDIUM", "HIGH", "CRITICAL"]))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"\nModel successfully trained and saved to: {MODEL_PATH}")

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm.tolist()
    }

if __name__ == "__main__":
    train_and_evaluate_model()
