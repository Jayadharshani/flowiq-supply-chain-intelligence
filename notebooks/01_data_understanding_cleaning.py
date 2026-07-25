{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ab6ae5aa",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd \n",
    "customers = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_customers_dataset.csv\")\n",
    "orders = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_orders_dataset.csv\")\n",
    "order_items = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_order_items_dataset.csv\")\n",
    "payments = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_order_payments_dataset.csv\")\n",
    "reviews = pd.read_csv(r\"c:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_order_reviews_dataset.csv\")\n",
    "products = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_products_dataset.csv\")\n",
    "sellers = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_sellers_dataset.csv\")\n",
    "category = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\product_category_name_translation.csv\")\n",
    "geolocation = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_geolocation_dataset.csv\")\n",
    "orders.head()\n",
    "orders.shape\n",
    "orders.info()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "12ac17ae",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "order_status\n",
      "delivered      96478\n",
      "shipped         1107\n",
      "canceled         625\n",
      "unavailable      609\n",
      "invoiced         314\n",
      "processing       301\n",
      "created            5\n",
      "approved           2\n",
      "Name: count, dtype: int64\n",
      "order_status\n",
      "shipped        1107\n",
      "canceled        619\n",
      "unavailable     609\n",
      "invoiced        314\n",
      "processing      301\n",
      "delivered         8\n",
      "created           5\n",
      "approved          2\n",
      "Name: count, dtype: int64\n"
     ]
    }
   ],
   "source": [
    "import pandas as pd\n",
    "\n",
    "orders = pd.read_csv(r\"C:\\Users\\user\\Downloads\\FLOWIQ\\data\\olist_orders_dataset.csv\")\n",
    "print(orders[\"order_status\"].value_counts())\n",
    "print(\n",
    "    orders[\n",
    "        orders[\"order_delivered_customer_date\"].isnull()\n",
    "    ][\"order_status\"].value_counts()\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "7aa88600",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "(96478, 8)\n"
     ]
    }
   ],
   "source": [
    "delivered_orders = orders[\n",
    "    orders[\"order_status\"] == \"delivered\"\n",
    "]\n",
    "\n",
    "print(delivered_orders.shape)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "57917e18",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "order_id                          0\n",
      "customer_id                       0\n",
      "order_status                      0\n",
      "order_purchase_timestamp          0\n",
      "order_approved_at                14\n",
      "order_delivered_carrier_date      2\n",
      "order_delivered_customer_date     8\n",
      "order_estimated_delivery_date     0\n",
      "dtype: int64\n"
     ]
    }
   ],
   "source": [
    "print(delivered_orders.isnull().sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "a470ac1e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "order_id                         0\n",
      "customer_id                      0\n",
      "order_status                     0\n",
      "order_purchase_timestamp         0\n",
      "order_approved_at                0\n",
      "order_delivered_carrier_date     0\n",
      "order_delivered_customer_date    0\n",
      "order_estimated_delivery_date    0\n",
      "dtype: int64\n",
      "(96455, 8)\n"
     ]
    }
   ],
   "source": [
    "delivered_orders = delivered_orders.dropna()\n",
    "\n",
    "print(delivered_orders.isnull().sum())\n",
    "\n",
    "print(delivered_orders.shape)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
