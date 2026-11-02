import pandas as pd

file_path = '/Users/xiang/Documents/PROJECT/Marketing/Customer Lifetime Value (CLV) & Tiered Loyalty Program/online_retail_dataset_CLV.xlsx'
df = pd.read_excel(file_path, sheet_name='online_retail')

df = df.dropna(subset=['CustomerID'])
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

clv_table = df.groupby('CustomerID').agg(
    Total_Revenue=('TotalPrice', 'sum'),
    Total_Orders=('InvoiceNo', 'nunique'),
    First_Purchase=('InvoiceDate', 'min'),
    Last_Purchase=('InvoiceDate', 'max')
).reset_index()

clv_table['Lifespan_Days'] = (clv_table['Last_Purchase'] - clv_table['First_Purchase']).dt.days
clv_table['Customer_Lifespan_Years'] = clv_table['Lifespan_Days'] / 365.0
clv_table['Customer_Lifespan_Years'] = clv_table['Customer_Lifespan_Years'].apply(lambda x: 1.0 if x == 0 else x)

clv_table['CLV'] = clv_table['Total_Revenue'] * clv_table['Customer_Lifespan_Years']

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

print("===== sample data (Top 10) =====")
print(clv_table[['CustomerID', 'Total_Revenue', 'Customer_Lifespan_Years', 'CLV', 'Customer_Tier']].sort_values(by='CLV', ascending=False).head(10))

print("\n===== Each Customer Tier Summary =====")
print(clv_table['Customer_Tier'].value_counts())

output_path = '/Users/xiang/Documents/PROJECT/Marketing/Customer Lifetime Value (CLV) & Tiered Loyalty Program/Customer_CLV_Tier_Output.xlsx'

clv_table.to_excel(output_path, index=False)







