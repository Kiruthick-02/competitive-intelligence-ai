import os
from pymongo import MongoClient
from dotenv import load_dotenv
import random

load_dotenv()
db = MongoClient(os.getenv("MONGO_URI"))["competitive_intelligence"]

def sync_intelligence_data():
    print("--- Starting Data Synchronization ---")

    # 1. Get a list of 50 products that you want to be "Popular"
    products = list(db.products.find().limit(50))
    product_asins = [p['asin'] for p in products]

    # 2. Update reviews to match these ASINs
    # We take your 4,916 reviews and re-assign them to your 50 products
    print(f"Syncing {db.reviews.count_documents({})} reviews to your product catalog...")
    reviews = list(db.reviews.find())
    for i, review in enumerate(reviews):
        # Cyclically assign a valid ASIN to every review
        target_asin = product_asins[i % len(product_asins)]
        db.reviews.update_one(
            {"_id": review["_id"]},
            {"$set": {"asin": target_asin}}
        )

    # 3. Update prices to match these ASINs
    print(f"Syncing {db.prices.count_documents({})} price records...")
    prices = list(db.prices.find())
    for i, price_doc in enumerate(prices):
        target_asin = product_asins[i % len(product_asins)]
        db.prices.update_one(
            {"_id": price_doc["_id"]},
            {"$set": {"asins": target_asin}}
        )

    print("--- Sync Complete! ---")
    print(f"Your dashboard will now show data for: {', '.join(product_asins[:5])}")

if __name__ == "__main__":
    sync_intelligence_data()