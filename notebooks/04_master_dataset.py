import pandas as pd

print("Loading Datasets...")

# ==========================================================
# LOAD DATASETS
# ==========================================================

orders = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_orders_dataset.csv")
customers = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_customers_dataset.csv")
order_items = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_order_items_dataset.csv")
products = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_products_dataset.csv")
payments = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_order_payments_dataset.csv")

print("All Datasets Loaded Successfully!")

# ==========================================================
# MERGE ORDERS + CUSTOMERS
# ==========================================================

print("\nMerging Orders + Customers...")

master_data = pd.merge(
    orders,
    customers,
    on="customer_id",
    how="left"
)

print("Shape:", master_data.shape)

# ==========================================================
# MERGE ORDER ITEMS
# ==========================================================

print("\nAdding Order Items...")

master_data = pd.merge(
    master_data,
    order_items,
    on="order_id",
    how="left"
)

print("Shape:", master_data.shape)

# ==========================================================
# MERGE PRODUCTS
# ==========================================================

print("\nAdding Products...")

master_data = pd.merge(
    master_data,
    products,
    on="product_id",
    how="left"
)

print("Shape:", master_data.shape)

# ==========================================================
# MERGE PAYMENTS
# ==========================================================

print("\nAdding Payments...")

master_data = pd.merge(
    master_data,
    payments,
    on="order_id",
    how="left"
)

print("Final Shape:", master_data.shape)

# ==========================================================
# PREVIEW
# ==========================================================

print("\nMaster Dataset Preview")
print(master_data.head())

print("\nColumns")
print(master_data.columns)

# ==========================================================
# MISSING VALUES
# ==========================================================

print("\nMissing Values")
print(master_data.isnull().sum())

# ==========================================================
# PAYMENT ANALYSIS
# ==========================================================

print("\nPayment Method Distribution")

payment_count = master_data["payment_type"].value_counts()

print(payment_count)

# ==========================================================
# SAVE MASTER DATASET
# ==========================================================

master_data.to_csv(
    r"C:\Users\user\Downloads\FLOWIQ\data\master_dataset.csv",
    index=False
)

print("\nMaster Dataset Saved Successfully!")
print("Location: C:\\Users\\user\\Downloads\\FLOWIQ\\data\\master_dataset.csv")