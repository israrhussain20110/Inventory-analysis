import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_inventory_data(num_samples=100):
    data = []
    start_date = datetime(2023, 1, 1)

    store_ids = [f'S{i:03d}' for i in range(1, 6)]
    product_ids = [f'P{i:04d}' for i in range(1, 21)]

    for _ in range(num_samples):
        store_id = random.choice(store_ids)
        product_id = random.choice(product_ids)
        date = start_date + timedelta(days=random.randint(0, 364))
        quantity = random.randint(10, 500)
        price = round(random.uniform(5.0, 100.0), 2)

        data.append({
            'Store ID': store_id,
            'Product ID': product_id,
            'Date': date.strftime('%Y-%m-%d'),
            'Quantity': quantity,
            'Price': price
        })

    df = pd.DataFrame(data)
    return df

def generate_stockouts_data(num_samples=70):
    data = []
    start_date = datetime(2023, 1, 1)

    store_ids = [f'S{i:03d}' for i in range(1, 6)]
    product_ids = [f'P{i:04d}' for i in range(1, 21)]

    for _ in range(num_samples):
        store_id = random.choice(store_ids)
        product_id = random.choice(product_ids)
        date = start_date + timedelta(days=random.randint(0, 364))
        stockout_quantity = random.randint(1, 50)

        data.append({
            'Store ID': store_id,
            'Product ID': product_id,
            'Date': date.strftime('%Y-%m-%d'),
            'Stockout Quantity': stockout_quantity
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    print("Generating sample inventory data...")
    inventory_df = generate_inventory_data(num_samples=100)
    inventory_df.to_csv('data/inventory.csv', index=False)
    print("Generated inventory.csv with 100 samples.")

    print("\nGenerating sample stockouts data...")
    stockouts_df = generate_stockouts_data(num_samples=70)
    stockouts_df.to_csv('data/stockouts.csv', index=False)
    print("Generated stockouts.csv with 70 samples.")
