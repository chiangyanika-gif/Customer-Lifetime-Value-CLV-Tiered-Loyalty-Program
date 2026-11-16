import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
file_path = BASE / 'online_retail_dataset_CLV.xlsx'
output_path = BASE / 'Customer_CLV_Tier_Python.xlsx'

df = pd.read_excel(file_path, sheet_name='online_retail')

# --- Cleaning ---
df = df.dropna(subset=['CustomerID'])
df['InvoiceNo'] = df['InvoiceNo'].astype(str)
df = df[~df['InvoiceNo'].str.startswith('C')]        # remove cancelled invoices
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]  # remove returns / invalid prices
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# --- Customer-level metrics ---
clv_table = df.groupby('CustomerID').agg(
    Total_Revenue=('TotalPrice', 'sum'),
    Total_Orders=('InvoiceNo', 'nunique'),
    First_Purchase=('InvoiceDate', 'min'),
    Last_Purchase=('InvoiceDate', 'max')
).reset_index()

clv_table['Lifespan_Days'] = (clv_table['Last_Purchase'] - clv_table['First_Purchase']).dt.days

# Historical CLV: total net revenue in the 12-month data window
clv_table['CLV'] = clv_table['Total_Revenue']

# --- Tiering by percentile ---
platinum_threshold = clv_table['CLV'].quantile(0.90)
gold_threshold = clv_table['CLV'].quantile(0.70)

def assign_tier(clv_value):
    if clv_value >= platinum_threshold:
        return 'Platinum'
    elif clv_value >= gold_threshold:
        return 'Gold'
    else:
        return 'Silver'

clv_table['Customer_Tier'] = clv_table['CLV'].apply(assign_tier)

print("===== Top 10 customers =====")
print(clv_table[['CustomerID', 'Total_Revenue', 'Total_Orders', 'CLV', 'Customer_Tier']]
      .sort_values(by='CLV', ascending=False).head(10))

print("\n===== Customers per tier =====")
print(clv_table['Customer_Tier'].value_counts())

print("\n===== CLV per tier =====")
print(clv_table.groupby('Customer_Tier')['CLV'].agg(['count', 'sum', 'mean']))

clv_table.to_excel(output_path, index=False)