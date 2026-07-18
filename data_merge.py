import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# LOAD DATASETS
# ==========================================================

orders = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_orders_dataset.csv")
customers = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_customers_dataset.csv")
order_items = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_order_items_dataset.csv")
products = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_products_dataset.csv")

print("Orders Dataset")
print(orders.head())

print("\nOrders Columns")
print(orders.columns)

# ==========================================================
# CUSTOMERS DATASET
# ==========================================================

print("\nCustomers Columns")
print(customers.columns)

# ==========================================================
# MERGE ORDERS + CUSTOMERS
# ==========================================================

merged_data = pd.merge(
    orders,
    customers,
    on="customer_id",
    how="inner"
)

print("\nMerged Dataset")
print(merged_data.head())

print("\nMerged Shape:")
print(merged_data.shape)

# ==========================================================
# TOP 10 CUSTOMER CITIES
# ==========================================================

top_cities = merged_data["customer_city"].value_counts().head(10)

print("\nTop 10 Customer Cities")
print(top_cities)

plt.figure(figsize=(10,5))
plt.bar(top_cities.index, top_cities.values)
plt.title("Top 10 Customer Cities")
plt.xlabel("Customer City")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ==========================================================
# ORDER ITEMS DATASET
# ==========================================================

print("\nOrder Items Columns")
print(order_items.columns)

# ==========================================================
# PRODUCTS DATASET
# ==========================================================

print("\nProducts Columns")
print(products.columns)

# ==========================================================
# MERGE ORDER ITEMS + PRODUCTS
# ==========================================================

product_data = pd.merge(
    order_items,
    products,
    on="product_id",
    how="inner"
)

print("\nMerged Product Dataset")
print(product_data.head())

print("\nProduct Dataset Shape:")
print(product_data.shape)

# ==========================================================
# TOP 10 PRODUCT CATEGORIES
# ==========================================================

top_products = (
    product_data["product_category_name"]
    .value_counts()
    .head(10)
)

print("\nTop 10 Product Categories")
print(top_products)

plt.figure(figsize=(12,6))
plt.bar(top_products.index, top_products.values)
plt.title("Top 10 Product Categories")
plt.xlabel("Product Category")
plt.ylabel("Number of Orders")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# ==========================================================
# COMPLETED
# ==========================================================

print("\n=======================================")
print("Data Merge Completed Successfully!")
print("=======================================")