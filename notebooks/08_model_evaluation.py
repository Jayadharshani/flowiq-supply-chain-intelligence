import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
 
print("=" * 60)
print("FLOWIQ - MODEL EVALUATION & COMPARISON")
print("=" * 60)
 
# ==========================================================
# LOAD PROCESSED DATASET
# ==========================================================
 
df = pd.read_csv(
    r"C:\Users\user\Downloads\FLOWIQ\data\processed_dataset.csv"
)
 
target = "late_delivery"
X = df.drop(columns=[target])
y = df[target]
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
 
# ==========================================================
# DEFINE MODELS TO COMPARE
# ==========================================================
 
models = {
    "Logistic Regression": LogisticRegression(
        class_weight="balanced", max_iter=1000, random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=12,
        class_weight="balanced", random_state=42, n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42
    ),
}
 
# ==========================================================
# CROSS-VALIDATION (more reliable than a single train/test split)
# ==========================================================
# 5-fold: the data is split into 5 parts, each model trains on 4
# and tests on the 5th, rotating through all 5. This tells us
# whether a model's score is consistently good, or just lucky on
# one particular split.
 
print("\nRunning 5-fold cross-validation (scored on F1)...")
 
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = []
 
for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=cv, scoring="f1", n_jobs=-1)
    cv_results.append({
        "Model": name,
        "CV F1 Mean": scores.mean(),
        "CV F1 Std": scores.std(),
    })
    print(f"{name}: F1 = {scores.mean():.4f} (+/- {scores.std():.4f})")
 
cv_results_df = pd.DataFrame(cv_results)
print("\nCross-validation summary (low Std = consistent, not lucky):")
print(cv_results_df.to_string(index=False))
 
# ==========================================================
# TRAIN + EVALUATE EACH MODEL (single held-out test set)
# ==========================================================
 
results = []
 
for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
 
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
 
    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1": f1_score(y_test, y_pred),
        "ROC-AUC": roc_auc_score(y_test, y_proba),
    })
 
    print(f"{name} done.")
 
# ==========================================================
# COMPARISON TABLE
# ==========================================================
 
results_df = pd.DataFrame(results).sort_values("F1", ascending=False)
results_df = results_df.merge(cv_results_df, on="Model")
 
print("\n" + "=" * 60)
print("MODEL COMPARISON (sorted by F1 score)")
print("=" * 60)
print(results_df.to_string(index=False))
 
# ==========================================================
# SAVE COMPARISON RESULTS
# ==========================================================
 
results_path = r"C:\Users\user\Downloads\FLOWIQ\notebooks\model_comparison_results.csv"
results_df.to_csv(results_path, index=False)
print(f"\nComparison results saved to: {results_path}")
 
# ==========================================================
# RETRAIN + SAVE THE BEST MODEL
# ==========================================================
 
best_model_name = results_df.iloc[0]["Model"]
best_model = models[best_model_name]
 
print(f"\nBest model: {best_model_name}")
print("Retraining best model on full training set and saving...")
 
best_model.fit(X_train, y_train)
 
best_model_path = r"C:\Users\user\Downloads\FLOWIQ\notebooks\best_model.pkl"
joblib.dump(best_model, best_model_path)
 
print(f"Best model saved to: {best_model_path}")
 
print("\nDone!")
print("=" * 60)
 