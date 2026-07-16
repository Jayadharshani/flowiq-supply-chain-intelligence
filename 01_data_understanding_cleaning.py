import pandas as pd 
customers = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_customers_dataset.csv")
orders = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_orders_dataset.csv")
order_items = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_order_items_dataset.csv")
payments = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_order_payments_dataset.csv")
reviews = pd.read_csv(r"c:\Users\user\Downloads\FLOWIQ\data\olist_order_reviews_dataset.csv")
products = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_products_dataset.csv")
sellers = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_sellers_dataset.csv")
category = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\product_category_name_translation.csv")
geolocation = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_geolocation_dataset.csv")
orders.head()
orders.shape
orders.info()
print(orders.info())

print(orders.head())
print("Shape:")
print(orders.shape)

print("\nColumns:")
print(orders.columns)

print("\nMissing Values:")
print(orders.isnull().sum())
print("\nData Types:")
print(orders.dtypes)
# Convert string columns to datetime

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

orders["order_approved_at"] = pd.to_datetime(
    orders["order_approved_at"]
)

orders["order_delivered_carrier_date"] = pd.to_datetime(
    orders["order_delivered_carrier_date"]
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)

orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"]
)
print("\nData Types After Conversion:")
print(orders.dtypes)
orders = pd.read_csv(r"C:\Users\user\Downloads\FLOWIQ\data\olist_orders_dataset.csv")
print(orders["order_status"].value_counts())
print(
    orders[
        orders["order_delivered_customer_date"].isnull()
    ]["order_status"].value_counts())
delivered_orders = orders[
    orders["order_status"] == "delivered"
]

print(delivered_orders.shape)
print(delivered_orders.isnull().sum())
delivered_orders = delivered_orders.dropna()

print(delivered_orders.isnull().sum())

print(delivered_orders.shape)