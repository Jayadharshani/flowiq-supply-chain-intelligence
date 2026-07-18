import pandas as pd
import matplotlib.pyplot as plt
# Load Dataset
orders = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_orders_dataset.csv")

# Keep only delivered orders
delivered_orders = orders[
    orders["order_status"] == "delivered"
].copy()

# Remove missing values
delivered_orders = delivered_orders.dropna()

# Convert date columns
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    delivered_orders[col] = pd.to_datetime(delivered_orders[col])

# Create delivery_days column
delivered_orders["delivery_days"] = (
    delivered_orders["order_delivered_customer_date"]
    - delivered_orders["order_purchase_timestamp"]
).dt.days

print("EDA Dataset Ready")
print(delivered_orders.head())
print("\nAverage Delivery Days:")
print(delivered_orders["delivery_days"].mean())
print("\nMinimum Delivery Days:")
print(delivered_orders["delivery_days"].min())
print("\nMaximum Delivery Days:")
print(delivered_orders["delivery_days"].max())
print("\nDelivery Days Summary:")
print(delivered_orders["delivery_days"].describe())
plt.hist(delivered_orders["delivery_days"], bins=30)

plt.title("Delivery Days Distribution")
plt.xlabel("Delivery Days")
plt.ylabel("Number of Orders")

plt.show()
delivered_orders["order_month"] = delivered_orders[
    "order_purchase_timestamp"
].dt.month_name()
monthly_orders = delivered_orders["order_month"].value_counts()

print(monthly_orders)
month_order = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

monthly_orders = (
    delivered_orders["order_month"]
    .value_counts()
    .reindex(month_order)
)

print(monthly_orders)
plt.figure(figsize=(10,5))

plt.bar(monthly_orders.index, monthly_orders.values)

plt.title("Orders by Month")
plt.xlabel("Month")
plt.ylabel("Number of Orders")

plt.xticks(rotation=45)

plt.show()
delivered_orders["delay_days"] = (
    delivered_orders["order_delivered_customer_date"]
    - delivered_orders["order_estimated_delivery_date"]
).dt.days
delivered_orders["late_delivery"] = (
    delivered_orders["delay_days"] > 0)
print(delivered_orders["late_delivery"].value_counts())
late_counts = delivered_orders["late_delivery"].value_counts()

plt.figure(figsize=(6,4))

plt.bar(
    ["On Time", "Late"],
    late_counts.values
)

plt.title("Late vs On-Time Deliveries")
plt.xlabel("Delivery Status")
plt.ylabel("Number of Orders")

plt.show()