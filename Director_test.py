import pandas as pd
import os
import random
from datetime import date, timedelta

# --- Configuration ---
SCRAPING_DATA_FOLDER = 'data/scraping_data'
SITE_NAME = 'Fastenal'
CSV_INPUT_FILENAME = 'grainger_products.csv'

PRODUCTS_CSV = os.path.join(SCRAPING_DATA_FOLDER, 'products.csv')
SNAPSHOTS_CSV = os.path.join(SCRAPING_DATA_FOLDER, 'price_inventory_snapshots.csv')
CSV_INPUT_PATH = os.path.join(SCRAPING_DATA_FOLDER, CSV_INPUT_FILENAME)

# Ensure the scraping data folder exists
os.makedirs(SCRAPING_DATA_FOLDER, exist_ok=True)

# --- Load product data from CSV ---
def load_products_from_csv(csv_path):
    df = pd.read_csv(csv_path)

    # Extract numeric price from string like "$0.3535 / each"
    df['Unit Price'] = df['Unit Price'].str.extract(r'([\d.]+)').astype(float)

    products = []
    for _, row in df.iterrows():
        products.append({
            "sku": str(row['SKU']),
            "price_per_unit": row['Unit Price'],
            "fastener_type": "hex bolt",
            "material": "steel",
            "grade_or_alloy": "unknown",
            "diameter_mm": None,
            "length_mm": None,
            "inventory": 1000,
            "manufacturer": "Fastenal."
        })
    return products

# --- Utilities ---
def get_current_date(snapshots_df):
    if snapshots_df.empty:
        return date.today()
    else:
        last_date = pd.to_datetime(snapshots_df['date_scraped']).max().date()
        return last_date + timedelta(days=1)

def simulate_daily_changes(products_df, snapshots_df, raw_products):
    today = get_current_date(snapshots_df)
    print(f"Simulating scrape for date: {today.strftime('%Y-%m-%d')}")

    output_data = []
    for product_data in raw_products:
        product_id = f"{SITE_NAME}_{product_data['sku']}"

        last_snapshot = snapshots_df[snapshots_df['product_id'] == product_id]
        if not last_snapshot.empty:
            last_inventory = last_snapshot.iloc[-1]['inventory_level']
            last_price = last_snapshot.iloc[-1]['price_per_unit']
        else:
            last_inventory = product_data['inventory']
            last_price = product_data['price_per_unit']

        # Simulate price fluctuation (optional)
        price_change = random.uniform(-0.03, 0.03)
        new_price = round(last_price * (1 + price_change), 4)

        new_inventory = last_inventory  # static or default

        new_data = product_data.copy()
        new_data['price_per_unit'] = new_price
        new_data['inventory'] = max(0, new_inventory)
        new_data['date_scraped'] = today
        output_data.append(new_data)

    return output_data

# --- Main ETL ---
def main():
    if os.path.exists(PRODUCTS_CSV):
        products_df = pd.read_csv(PRODUCTS_CSV)
    else:
        products_df = pd.DataFrame(columns=[
            'product_id', 'site', 'sku', 'fastener_type', 'material',
            'grade_or_alloy', 'diameter_mm', 'length_mm', 'manufacturer',
            'first_seen_date', 'last_seen_date'])

    if os.path.exists(SNAPSHOTS_CSV):
        snapshots_df = pd.read_csv(SNAPSHOTS_CSV)
    else:
        snapshots_df = pd.DataFrame(columns=[
            'snapshot_id', 'product_id', 'date_scraped', 'price_per_unit', 'inventory_level'])

    raw_products = load_products_from_csv(CSV_INPUT_PATH)
    scraped_data = simulate_daily_changes(products_df, snapshots_df, raw_products)
    today_str = scraped_data[0]['date_scraped'].strftime('%Y-%m-%d')

    new_products = []
    new_snapshots = []

    for item in scraped_data:
        product_id = f"{SITE_NAME}_{item['sku']}"

        if product_id not in products_df['product_id'].values:
            print(f"  -> New product found: {product_id}. Adding to products table.")
            new_product = {
                'product_id': product_id,
                'site': SITE_NAME,
                'sku': item['sku'],
                'fastener_type': item['fastener_type'],
                'material': item['material'],
                'grade_or_alloy': item['grade_or_alloy'],
                'diameter_mm': item['diameter_mm'],
                'length_mm': item['length_mm'],
                'manufacturer': item['manufacturer'],
                'first_seen_date': today_str,
                'last_seen_date': today_str
            }
            new_products.append(new_product)
        else:
            products_df.loc[products_df['product_id'] == product_id, 'last_seen_date'] = today_str

        new_snapshot = {
            'product_id': product_id,
            'date_scraped': today_str,
            'price_per_unit': item['price_per_unit'],
            'inventory_level': item['inventory']
        }
        new_snapshots.append(new_snapshot)

    if new_products:
        products_df = pd.concat([products_df, pd.DataFrame(new_products)], ignore_index=True)

    if new_snapshots:
        new_snapshots_df = pd.DataFrame(new_snapshots)
        last_id = snapshots_df['snapshot_id'].max() if not snapshots_df.empty else -1
        new_snapshots_df['snapshot_id'] = range(last_id + 1, last_id + 1 + len(new_snapshots_df))
        snapshots_df = pd.concat([snapshots_df, new_snapshots_df], ignore_index=True)

    products_df.to_csv(PRODUCTS_CSV, index=False)
    snapshots_df.to_csv(SNAPSHOTS_CSV, index=False)

    print("\nDaily scrape simulation complete. CSV files have been updated.")
    print(f"Total products: {len(products_df)}")
    print(f"Total snapshots: {len(snapshots_df)}")

if __name__ == "__main__":
    main()
