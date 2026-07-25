import pandas as pd
import numpy as np

print("=" * 60)
print("FLOWIQ - FEATURE ENGINEERING")
print("=" * 60)

DATA_DIR = r"C:\Users\user\Downloads\FLOWIQ\data"

print("\nLoading raw datasets...")

orders = pd.read_csv(fr"{DATA_DIR}\olist_orders_dataset.csv")
customers = pd.read_csv(fr"{DATA_DIR}\olist_customers_dataset.csv")
order_items = pd.read_csv(fr"{DATA_DIR}\olist_order_items_dataset.csv")
products = pd.read_csv(fr"{DATA_DIR}\olist_products_dataset.csv")
payments = pd.read_csv(fr"{DATA_DIR}\olist_order_payments_dataset.csv")

print("Merging...")

master_data = pd.merge(orders, customers, on="customer_id", how="left")
master_data = pd.merge(master_data, order_items, on="order_id", how="left")
master_data = pd.merge(master_data, products, on="product_id", how="left")
master_data = pd.merge(master_data, payments, on="order_id", how="left")

print("Merged Successfully!")
print(master_data.shape)

date_columns = [
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date", "shipping_limit_date"
]
for col in date_columns:
    if col in master_data.columns:
        master_data[col] = pd.to_datetime(master_data[col], errors="coerce")

master_data.drop_duplicates(inplace=True)

numeric_columns = master_data.select_dtypes(include=["number"]).columns
for col in numeric_columns:
    master_data[col] = master_data[col].fillna(master_data[col].median())

categorical_columns = master_data.select_dtypes(include=["object"]).columns
for col in categorical_columns:
    master_data[col] = master_data[col].fillna("Unknown")

print("\nCreating Features...")

master_data["delivery_days"] = (
    master_data["order_delivered_customer_date"] - master_data["order_purchase_timestamp"]
).dt.days

master_data["estimated_days"] = (
    master_data["order_estimated_delivery_date"] - master_data["order_purchase_timestamp"]
).dt.days

master_data["late_delivery"] = np.where(
    master_data["order_status"] == "delivered",
    (master_data["delivery_days"] > master_data["estimated_days"]).astype(int),
    np.nan
)

master_data["purchase_year"] = master_data["order_purchase_timestamp"].dt.year
master_data["purchase_month"] = master_data["order_purchase_timestamp"].dt.month
master_data["purchase_day"] = master_data["order_purchase_timestamp"].dt.day
master_data["purchase_hour"] = master_data["order_purchase_timestamp"].dt.hour
master_data["purchase_weekday"] = master_data["order_purchase_timestamp"].dt.dayofweek

master_data["total_order_value"] = master_data["price"] + master_data["freight_value"]

master_data["product_volume"] = (
    master_data["product_length_cm"] * master_data["product_width_cm"] * master_data["product_height_cm"]
)

master_data["heavy_product"] = (master_data["product_weight_g"] > 5000).astype(int)
master_data["multiple_installments"] = (master_data["payment_installments"] > 1).astype(int)

print("\nFinal Shape:", master_data.shape)
print("\nlate_delivery breakdown (NaN = not yet/never delivered):")
print(master_data["late_delivery"].value_counts(dropna=False))

save_path = fr"{DATA_DIR}\..\notebooks\master_dataset_features.csv"
master_data.to_csv(save_path, index=False)

print("\nFeature Dataset Saved Successfully!")
print(save_path)

print("\nDone!")
print("=" * 60)