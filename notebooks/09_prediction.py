import pandas as pd
import joblib
from datetime import datetime
 
print("=" * 60)
print("FLOWIQ - DELAY PREDICTION")
print("=" * 60)
 
NOTEBOOKS_DIR = r"C:\Users\user\Downloads\FLOWIQ\notebooks"
 
# ==========================================================
# LOAD SAVED MODEL + PREPROCESSING ARTIFACTS
# ==========================================================
# These 4 files together are what make a correct prediction possible:
#   - best_model.pkl      -> the trained brain
#   - scaler.pkl           -> same mean/std used during training
#   - label_encoders.pkl   -> same category-to-number mapping per column
#   - feature_columns.pkl  -> exact column order the model expects
 
print("\nLoading model and preprocessing artifacts...")
 
model = joblib.load(fr"{NOTEBOOKS_DIR}\best_model.pkl")
scaler = joblib.load(fr"{NOTEBOOKS_DIR}\scaler.pkl")
encoders = joblib.load(fr"{NOTEBOOKS_DIR}\label_encoders.pkl")
feature_columns = joblib.load(fr"{NOTEBOOKS_DIR}\feature_columns.pkl")
 
print("Loaded successfully!")
 
 
def engineer_features(order: dict) -> dict:
    """
    Takes one raw new order (plain values a human would type in) and
    computes the same derived features 05_feature_engineering.py
    created during training. Must stay in sync with that script.
    """
    purchase_ts = pd.to_datetime(order["order_purchase_timestamp"])
    estimated_ts = pd.to_datetime(order["order_estimated_delivery_date"])
 
    features = dict(order)  # copy raw fields forward
 
    features["purchase_year"] = purchase_ts.year
    features["purchase_month"] = purchase_ts.month
    features["purchase_day"] = purchase_ts.day
    features["purchase_hour"] = purchase_ts.hour
    features["purchase_weekday"] = purchase_ts.dayofweek
 
    features["total_order_value"] = order["price"] + order["freight_value"]
 
    features["product_volume"] = (
        order["product_length_cm"] * order["product_width_cm"] * order["product_height_cm"]
    )
 
    features["heavy_product"] = int(order["product_weight_g"] > 5000)
    features["multiple_installments"] = int(order["payment_installments"] > 1)
 
    # Convert to same epoch-seconds numeric format 06_data_preprocessing.py used
    features["order_purchase_timestamp"] = int(purchase_ts.timestamp())
    features["order_estimated_delivery_date"] = int(estimated_ts.timestamp())
 
    return features
 
 
def encode_categoricals(features: dict) -> dict:
    """
    Encodes text categories using the SAVED encoders from training -
    not fresh ones. If a category was never seen during training
    (e.g. a brand-new city), we fall back to -1 so the model at
    least gets a valid number instead of crashing.
    """
    encoded = dict(features)
    for col, le in encoders.items():
        if col in encoded:
            value = str(encoded[col])
            if value in le.classes_:
                encoded[col] = le.transform([value])[0]
            else:
                print(f"Warning: unseen value '{value}' for '{col}', using fallback.")
                encoded[col] = -1
    return encoded
 
 
def predict_delay(order: dict) -> dict:
    """
    Full pipeline: raw order -> engineered features -> encoded ->
    scaled -> prediction. Returns a readable result, not raw numbers.
    """
    features = engineer_features(order)
    features = encode_categoricals(features)
 
    # Build a single-row DataFrame in the EXACT column order the
    # model was trained on - order matters for scaler and model alike.
    row = pd.DataFrame([features])[feature_columns]
 
    scaled_row = scaler.transform(row)
    scaled_row = pd.DataFrame(scaled_row, columns=feature_columns)
 
    prediction = model.predict(scaled_row)[0]
    probability = model.predict_proba(scaled_row)[0][1]  # P(late)
 
    return {
        "late_delivery_predicted": bool(prediction),
        "late_probability": round(float(probability), 4),
        "risk_level": (
            "HIGH" if probability >= 0.6 else
            "MEDIUM" if probability >= 0.3 else
            "LOW"
        )
    }
 
 
# ==========================================================
# EXAMPLE - a new order (edit these values to test others)
# ==========================================================
 
if __name__ == "__main__":
    sample_order = {
        "order_purchase_timestamp": "2018-05-14 10:30:00",
        "order_estimated_delivery_date": "2018-05-25 00:00:00",
        "customer_zip_code_prefix": 3149,
        "customer_city": "sao paulo",
        "customer_state": "SP",
        "order_item_id": 1,
        "price": 89.90,
        "freight_value": 15.50,
        "product_category_name": "utilidades_domesticas",
        "product_name_lenght": 40,
        "product_description_lenght": 268,
        "product_photos_qty": 4,
        "product_weight_g": 1200,
        "product_length_cm": 20,
        "product_height_cm": 10,
        "product_width_cm": 15,
        "payment_sequential": 1,
        "payment_type": "credit_card",
        "payment_installments": 3,
        "payment_value": 105.40,
    }
 
    print("\nPredicting delay for sample order...")
    result = predict_delay(sample_order)
 
    print("\n" + "=" * 60)
    print("PREDICTION RESULT")
    print("=" * 60)
    for key, value in result.items():
        print(f"{key}: {value}")
 
    print("\nDone!")
    print("=" * 60)