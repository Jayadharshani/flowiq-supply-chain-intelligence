from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd
import joblib
 
from database import engine, Base, get_db
from DB_models import PredictionHistory, User
from AUTH import (
    hash_password, verify_password, create_access_token, get_current_user
)
 
# ==========================================================
# CREATE DATABASE TABLES (IF THEY DON'T EXIST YET)
# ==========================================================
# This reads every class that inherits from Base (currently just
# PredictionHistory in models.py) and creates the matching table
# in the database if it isn't already there. Safe to run every
# time the server starts - it won't wipe existing data.
 
Base.metadata.create_all(bind=engine)
 
# ==========================================================
# LOAD MODEL + PREPROCESSING ARTIFACTS (ONCE, AT STARTUP)
# ==========================================================
# This happens ONE time when the server starts, not on every
# request - loading a .pkl file is relatively slow, so we don't
# want to repeat it for every single prediction.
 
import os
 
# BASE_DIR = the folder this app.py file lives in (backend/).
# Using a path relative to this file - instead of a hardcoded
# Windows path - means the exact same code works locally on
# Windows AND on Render's Linux servers without any changes.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "..", "notebooks")
 
model = joblib.load(os.path.join(NOTEBOOKS_DIR, "best_model.pkl"))
scaler = joblib.load(os.path.join(NOTEBOOKS_DIR, "scaler.pkl"))
encoders = joblib.load(os.path.join(NOTEBOOKS_DIR, "label_encoders.pkl"))
feature_columns = joblib.load(os.path.join(NOTEBOOKS_DIR, "feature_columns.pkl"))
 
# A handful of REAL orders from the training data, kept in memory so
# the frontend can offer them as ready-made templates ("load a sample
# order") instead of one single hardcoded example. Only raw/original
# fields are kept - not the engineered ones (purchase_month, etc.),
# since the frontend recomputes those itself from the raw values.
_raw_sample_columns = [
    "order_purchase_timestamp", "order_estimated_delivery_date",
    "customer_zip_code_prefix", "customer_city", "customer_state",
    "order_item_id", "price", "freight_value", "product_category_name",
    "product_name_lenght", "product_description_lenght", "product_photos_qty",
    "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm",
    "payment_sequential", "payment_type", "payment_installments", "payment_value",
]
_full_dataset = pd.read_csv(os.path.join(NOTEBOOKS_DIR, "master_dataset_features.csv"))
_delivered_only = _full_dataset[_full_dataset["order_status"] == "delivered"]
sample_orders_df = (
    _delivered_only[_raw_sample_columns]
    .drop_duplicates(subset=["customer_city", "product_category_name"])
    .sample(n=min(30, len(_delivered_only)), random_state=42)
    .reset_index(drop=True)
)
 
print("Model and preprocessing artifacts loaded.")
 
# ==========================================================
# CREATE THE FASTAPI APP
# ==========================================================
 
app = FastAPI(title="FlowIQ Delay Prediction API")
 
# CORS: without this, a frontend running on a different
# origin (e.g. http://localhost:5173 for React) would be
# BLOCKED by the browser from calling this API, even though
# the request itself is valid. This opens it up for development.
# Before deployment, replace "*" with your actual frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
# ==========================================================
# REQUEST SCHEMA (PYDANTIC MODEL)
# ==========================================================
# This defines exactly what a valid request must look like.
# FastAPI uses this to auto-validate incoming JSON, auto-generate
# API docs, and reject malformed requests before your code runs.
 
class OrderInput(BaseModel):
    order_purchase_timestamp: str        # e.g. "2018-05-14 10:30:00"
    order_estimated_delivery_date: str   # e.g. "2018-05-25 00:00:00"
    customer_zip_code_prefix: int
    customer_city: str
    customer_state: str
    order_item_id: int
    price: float
    freight_value: float
    product_category_name: str
    product_name_lenght: float
    product_description_lenght: float
    product_photos_qty: float
    product_weight_g: float
    product_length_cm: float
    product_height_cm: float
    product_width_cm: float
    payment_sequential: int
    payment_type: str
    payment_installments: int
    payment_value: float
 
 
class PredictionHistoryOut(BaseModel):
    id: int
    customer_city: str
    customer_state: str
    product_category_name: str
    price: float
    freight_value: float
    payment_type: str
    late_delivery_predicted: bool
    late_probability: float
    risk_level: str
 
    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object directly
 
 
# ==========================================================
# SAME PREDICTION LOGIC AS 09_prediction.py
# ==========================================================
 
def engineer_features(order: dict) -> dict:
    purchase_ts = pd.to_datetime(order["order_purchase_timestamp"])
    estimated_ts = pd.to_datetime(order["order_estimated_delivery_date"])
 
    features = dict(order)
 
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
 
    features["order_purchase_timestamp"] = int(purchase_ts.timestamp())
    features["order_estimated_delivery_date"] = int(estimated_ts.timestamp())
 
    return features
 
 
def encode_categoricals(features: dict) -> tuple[dict, list]:
    """
    Returns (encoded_features, unseen_fields).
    unseen_fields lists which columns had a value never seen during
    training - e.g. a city that isn't in the Olist dataset. The
    caller uses this to warn the user instead of silently returning
    a confident-looking prediction based on a guessed value.
    """
    encoded = dict(features)
    unseen_fields = []
    for col, le in encoders.items():
        if col in encoded:
            value = str(encoded[col])
            if value in le.classes_:
                encoded[col] = le.transform([value])[0]
            else:
                encoded[col] = -1
                unseen_fields.append(col)
    return encoded, unseen_fields
 
 
def predict_delay(order: dict) -> dict:
    features = engineer_features(order)
    features, unseen_fields = encode_categoricals(features)
 
    row = pd.DataFrame([features])[feature_columns]
    scaled_row = scaler.transform(row)
    scaled_row = pd.DataFrame(scaled_row, columns=feature_columns)
 
    prediction = model.predict(scaled_row)[0]
    probability = model.predict_proba(scaled_row)[0][1]
 
    warning = None
    if unseen_fields:
        field_list = ", ".join(unseen_fields)
        warning = (
            f"The value(s) for [{field_list}] were not seen during training "
            f"(the model was trained on Brazilian Olist marketplace data). "
            f"This prediction is a rough guess and should not be trusted."
        )
 
    return {
        "late_delivery_predicted": bool(prediction),
        "late_probability": round(float(probability), 4),
        "risk_level": (
            "HIGH" if probability >= 0.6 else
            "MEDIUM" if probability >= 0.3 else
            "LOW"
        ),
        "warning": warning,
    }
 
 
# ==========================================================
# API ENDPOINTS
# ==========================================================
 
@app.get("/")
def root():
    """Simple check to confirm the server is running."""
    return {"status": "FlowIQ API is running"}
 
 
@app.get("/health")
def health_check():
    """Used by monitoring tools / load balancers to check the API is alive."""
    return {"status": "ok"}
 
 
@app.get("/options")
def get_options():
    """
    Returns every valid value the model actually saw during training,
    for each categorical field (city, state, category, payment type).
    The frontend uses this to show dropdowns instead of free-text
    inputs - so a user can only pick values the model understands,
    instead of typing something like 'karaikal' that was never in
    the training data and produces an unreliable guess.
    """
    return {
        col: sorted(le.classes_.tolist())
        for col, le in encoders.items()
    }
 
 
@app.get("/sample-orders")
def get_sample_orders():
    """
    Returns ~30 real orders from the training dataset, so the
    frontend can offer them as ready-made starting templates - pick
    one and the whole form fills in with that order's actual values,
    instead of always starting from one single hardcoded example.
    """
    return sample_orders_df.to_dict(orient="records")
 
 
# ==========================================================
# AUTH ENDPOINTS
# ==========================================================
 
class RegisterInput(BaseModel):
    username: str
    password: str
 
 
@app.post("/register")
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    """
    Creates a new user account. The password is hashed before
    being stored - the plain password itself is never saved anywhere.
    """
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
 
    new_user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}
 
 
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Checks username/password, and if correct, returns a signed JWT
    token. The frontend stores this token and sends it back with
    every future request to prove the user is logged in.
 
    Uses OAuth2PasswordRequestForm (not a plain JSON body) because
    that's the standard FastAPI expects for the auto-generated
    /docs "Authorize" button to work correctly.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
 
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
 
 
@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently logged-in user - useful for the frontend
    to check 'am I still logged in?' when the app loads."""
    return {"id": current_user.id, "username": current_user.username}
 
 
# ==========================================================
# PREDICTION ENDPOINTS (PROTECTED - LOGIN REQUIRED)
# ==========================================================
 
 
@app.post("/predict")
def predict(
    order: OrderInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Main endpoint. Requires a valid login token. Accepts one order's
    details as JSON, returns a delay prediction, AND saves it to the
    database (linked to the logged-in user) so it shows up in
    prediction history / dashboard later.
    """
    try:
        order_dict = order.model_dump()
        result = predict_delay(order_dict)
 
        # Save this prediction as a new row in prediction_history
        history_entry = PredictionHistory(
            user_id=current_user.id,
            customer_city=order_dict["customer_city"],
            customer_state=order_dict["customer_state"],
            product_category_name=order_dict["product_category_name"],
            price=order_dict["price"],
            freight_value=order_dict["freight_value"],
            payment_type=order_dict["payment_type"],
            late_delivery_predicted=result["late_delivery_predicted"],
            late_probability=result["late_probability"],
            risk_level=result["risk_level"],
        )
        db.add(history_entry)
        db.commit()
 
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get("/history", response_model=list[PredictionHistoryOut])
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the CURRENT USER's most recent predictions, newest first.
    Requires login - each user only sees their own history.
    """
    records = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(desc(PredictionHistory.created_at))
        .limit(limit)
        .all()
    )
    return records
 
 
# ==========================================================
# RUN THE SERVER (for local development)
# ==========================================================
# In production you'd normally run uvicorn from the command line
# instead, but this lets you just do `python app.py` to test locally.
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)