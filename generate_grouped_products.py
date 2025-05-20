import pandas as pd
import re

# Load your matched CSV
df = pd.read_csv('matched_products.csv')

# Function to clean product names to a base category
def extract_base_product(name):
    # Remove flavors and extra details after size
    name = re.sub(r'(чоколадо|јагода|солена карамела|карамела|колаче|ф\'стак|ванила|малинка|кокос|смути|сант|п.к|\.)', '', name, flags=re.IGNORECASE)
    # Keep only up to the size like '50ГР' or '0.5Л'
    match = re.search(r'^(.+?\d+(\.\d+)?\s*(гр|л|ml|мл|g|l))', name, flags=re.IGNORECASE)
    return match.group(1).strip() if match else name.strip()

# Process product1 only
df['base_product'] = df['product1'].apply(extract_base_product)
df['market'] = df['market1']
df['price'] = df['price1']

# Aggregate to average price per base product and market
summary = df.groupby(['base_product', 'market']).agg({'price': 'mean'}).reset_index()
summary.rename(columns={'price': 'average_price'}, inplace=True)

# Save as grouped_products.csv
summary.to_csv('grouped_products.csv', index=False, encoding='utf-8')
print("✅ grouped_products.csv generated successfully.")
