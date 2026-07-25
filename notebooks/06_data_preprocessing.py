import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
 
print("=" * 60)
print("FLOWIQ - DATA PREPROCESSING")
print("=" * 60)
 
# ==========================================================
# LOAD FEATURE DATASET
# ==========================================================
 
print("\nLoading Feature Dataset...")
 
df = pd.read_csv(
    r"C:\Users\user\Downloads\FLOWIQ\notebooks\master_dataset_features.csv"
)
 
print("Dataset Loaded Successfully!")
print("Shape :", df.shape)
 
# ==========================================================
# RE-PARSE DATE COLUMNS
# ==========================================================
# CSV files don't preserve datetime type - order_purchase_timestamp
# and order_estimated_delivery_date come back as plain text strings
# after pd.read_csv(). If left as-is, the categorical-encoding step
# below would wrongly treat each unique timestamp as a random
# category instead of a real time value. Converting back to
# datetime here ensures they go through proper epoch-second
# conversion further down, matching what 09_prediction.py does.
 
date_columns_to_restore = ["order_purchase_timestamp", "order_estimated_delivery_date"]
for col in date_columns_to_restore:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
 
# ==========================================================
# KEEP ONLY DELIVERED ORDERS
# ==========================================================
 
df = df[df["order_status"] == "delivered"].copy()
print("After filtering to delivered orders:", df.shape)
 
# ==========================================================
# DROP UNNECESSARY / LEAKAGE COLUMNS
# ==========================================================
 
print("\nDropping ID and leakage columns...")
 
drop_columns = [
    "order_id", "customer_id", "customer_unique_id", "product_id", "seller_id",
    "order_delivered_customer_date", "order_delivered_carrier_date",
    "order_approved_at", "shipping_limit_date",
    "delivery_days", "estimated_days",
    "order_status",
]
 
for col in drop_columns:
    if col in df.columns:
        df.drop(columns=col, inplace=True)
 
print("Remaining Shape :", df.shape)
 
# ==========================================================
# ENCODE CATEGORICAL COLUMNS
# ==========================================================
# We save one LabelEncoder PER column (not a shared one) so
# 09_prediction.py can encode a brand-new order's categories
# using the exact same mapping the model was trained on.
 
print("\nEncoding Categorical Columns...")
 
categorical_columns = df.select_dtypes(include=["object"]).columns
encoders = {}
 
for col in categorical_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le
 
print("Encoding Completed!")
 
# ==========================================================
# CONVERT REMAINING DATETIME COLUMNS
# ==========================================================
 
datetime_columns = df.select_dtypes(include=["datetime64[ns]"]).columns
for col in datetime_columns:
    df[col] = df[col].astype("int64") // 10**9
 
# ==========================================================
# SELECT TARGET COLUMN
# ==========================================================
 
target = "late_delivery"
 
X = df.drop(columns=[target])
y = df[target].astype(int)
 
print("\nFeatures Shape :", X.shape)
print("Target Shape :", y.shape)
print("Target balance:\n", y.value_counts(normalize=True))
 
# ==========================================================
# FEATURE SCALING
# ==========================================================
# We save the fitted scaler too, so a new order gets scaled
# using the exact same mean/std the model was trained on -
# NOT a fresh scaler fit on just that one new row.
 
print("\nScaling Numerical Features...")
 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
 
print("Scaling Completed!")
 
# ==========================================================
# FINAL DATASET
# ==========================================================
 
processed_data = X_scaled.copy()
processed_data[target] = y.values
 
print("\nProcessed Dataset Shape:", processed_data.shape)
 
# ==========================================================
# SAVE DATASET + SCALER + ENCODERS + COLUMN ORDER
# ==========================================================
 
save_path = r"C:\Users\user\Downloads\FLOWIQ\data\processed_dataset.csv"
processed_data.to_csv(save_path, index=False)
print("\nProcessed Dataset Saved Successfully!")
print(save_path)
 
NOTEBOOKS_DIR = r"C:\Users\user\Downloads\FLOWIQ\notebooks"
 
joblib.dump(scaler, fr"{NOTEBOOKS_DIR}\scaler.pkl")
print(f"Scaler saved: {NOTEBOOKS_DIR}\\scaler.pkl")
 
joblib.dump(encoders, fr"{NOTEBOOKS_DIR}\label_encoders.pkl")
print(f"Label encoders saved: {NOTEBOOKS_DIR}\\label_encoders.pkl")
 
joblib.dump(list(X.columns), fr"{NOTEBOOKS_DIR}\feature_columns.pkl")
print(f"Feature column order saved: {NOTEBOOKS_DIR}\\feature_columns.pkl")
 
print("\nDone!")
print("=" * 60)