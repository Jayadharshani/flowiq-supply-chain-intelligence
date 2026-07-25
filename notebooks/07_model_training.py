import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
 
print("=" * 60)
print("FLOWIQ - MODEL TRAINING")
print("=" * 60)
 
# ==========================================================
# LOAD PROCESSED DATASET
# ==========================================================
 
print("\nLoading Processed Dataset...")
 
df = pd.read_csv(
    r"C:\Users\user\Downloads\FLOWIQ\data\processed_dataset.csv"
)
 
print("Shape:", df.shape)
 
# ==========================================================
# SPLIT FEATURES / TARGET
# ==========================================================
 
target = "late_delivery"
X = df.drop(columns=[target])
y = df[target]
 
print("\nTarget distribution:")
print(y.value_counts(normalize=True))
 
# ==========================================================
# TRAIN / TEST SPLIT
# ==========================================================
# stratify=y keeps the same late/on-time ratio in both splits -
# important here since late orders are a minority class (~7-8%).
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
 
print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)
 
# ==========================================================
# TRAIN MODEL
# ==========================================================
 
print("\nTraining RandomForestClassifier...")
 
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    class_weight="balanced",   # compensates for late-delivery being a minority class
    random_state=42,
    n_jobs=-1
)
 
model.fit(X_train, y_train)
 
print("Training Completed!")
 
# ==========================================================
# EVALUATE
# ==========================================================
 
y_pred = model.predict(X_test)
 
print("\nAccuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("F1 Score :", f1_score(y_test, y_pred))
 
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
 
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
 
# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================
 
importance = pd.Series(model.feature_importances_, index=X.columns)
importance = importance.sort_values(ascending=False)
 
print("\nTop 10 Most Important Features:")
print(importance.head(10))
 
# ==========================================================
# SAVE MODEL
# ==========================================================
 
model_path = r"C:\Users\user\Downloads\FLOWIQ\notebooks\late_delivery_model.pkl"
joblib.dump(model, model_path)
 
print("\nModel Saved Successfully!")
print(model_path)
 
print("\nDone!")
print("=" * 60)
