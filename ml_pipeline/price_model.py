import os
import pandas as pd
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")


def run_price_analysis():

    print("Connecting to MongoDB...")

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    print("Starting Price Trend Analysis...")

    prices_cursor = db.prices.find({})

    records = []
    count = 0

    for item in prices_cursor:

        count += 1

        if count % 10000 == 0:
            print(f"Processed {count} records...")

        asins_field = item.get("asins", "")
        asin_list = asins_field.split(",") if isinstance(asins_field, str) else [asins_field]

        price_info = item.get("prices", {})

        if not price_info:
            continue

        for asin in asin_list:

            clean_asin = str(asin).strip()

            if not clean_asin:
                continue

            date_val = price_info.get("dateSeen")

            if isinstance(date_val, list):
                date_val = date_val[0]

            records.append({
                "_id": item["_id"],
                "asin": clean_asin,
                "price": price_info.get("amountMax", 0),
                "date": date_val
            })

    if not records:
        print("No valid price records found.")
        return

    print(f"Total records collected: {len(records)}")

    df = pd.DataFrame(records)

    print("Cleaning and preparing data...")

    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')

    df = df.dropna(subset=['date', 'price'])

    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['price'])

    df = df.sort_values(by=['asin', 'date'])

    print("Analyzing price trends...")

    operations = []

    processed = 0

    for asin, product_prices in df.groupby('asin'):

        if len(product_prices) == 1:
            first_price = last_price = float(product_prices['price'].iloc[0])
        else:
            first_price = float(product_prices['price'].iloc[0])
            last_price = float(product_prices['price'].iloc[-1])

        price_change = last_price - first_price

        discount_percentage = (
            ((last_price - first_price) / first_price) * 100
            if first_price > 0 else 0
        )

        price_volatility = product_prices['price'].std()

        trend = "Stable"

        if discount_percentage <= -5:
            trend = "Price Drop Detected"

        elif discount_percentage >= 5:
            trend = "Price Increase Detected"

        for _, row in product_prices.iterrows():

            operations.append(
                UpdateOne(
                    {"_id": row["_id"]},
                    {
                        "$set": {
                            "pricing_intelligence": {
                                "asin": asin,
                                "latest_price": float(last_price),
                                "price_change": float(price_change),
                                "discount_percentage": float(discount_percentage),
                                "price_volatility": float(price_volatility) if pd.notna(price_volatility) else 0.0,
                                "trend": trend,
                                "analysis_date": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                    }
                )
            )

            processed += 1

            if processed % 5000 == 0:
                print(f"Prepared updates for {processed} records...")

    print("Updating MongoDB records...")

    if operations:
        db.prices.bulk_write(operations)

    print("--------------------------------------------------")
    print("Price Analysis Complete.")
    print(f"Total records updated: {processed}")
    print("--------------------------------------------------")

    client.close()


if __name__ == "__main__":
    run_price_analysis()