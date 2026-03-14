import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import warnings

# Suppress the mixed date format warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")

def run_price_analysis():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    print("Starting Price Trend Analysis...")
    
    prices_data = list(db.prices.find({}))
    if not prices_data:
        print("No price data found in the database.")
        return

    # Flatten nested data into a list of records
    records = []
    for item in prices_data:
        # Handle cases where multiple ASINs are in one string (e.g., "B001, B002")
        asins_field = item.get("asins", "")
        asin_list = asins_field.split(",") if isinstance(asins_field, str) else [asins_field]
        
        price_info = item.get("prices", {})
        if not price_info: continue

        for asin in asin_list:
            clean_asin = asin.strip()
            if not clean_asin: continue
            
            # Extract date - handle if it's a list or a comma-string
            date_val = price_info.get("dateSeen")
            if isinstance(date_val, list): date_val = date_val[0]
            
            records.append({
                "asin": clean_asin,
                "price": price_info.get("amountMax", 0),
                "date": date_val
            })

    df = pd.DataFrame(records)
    
    # --- FIX FOR THE DATE WARNING ---
    # We use format='mixed' to handle the various ISO formats in the CSV
    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df = df.dropna(subset=['date', 'price']).sort_values(by='date')

    unique_asins = df['asin'].unique()
    updated_count = 0
    
    for asin in unique_asins:
        product_prices = df[df['asin'] == asin]
        
        if len(product_prices) < 2:
            continue
            
        first_price = float(product_prices['price'].iloc[0])
        last_price = float(product_prices['price'].iloc[-1])
        
        # Calculate features
        price_change = last_price - first_price
        discount_percentage = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
        price_volatility = product_prices['price'].std()
        
        trend = "Stable"
        if discount_percentage <= -5:
            trend = "Price Drop Detected"
        elif discount_percentage >= 5:
            trend = "Price Increase Detected"

        # Update or Upsert intelligence into the insights collection
        db.insights.update_one(
            {"asin": asin},
            {"$set": {
                "pricing_intelligence": {
                    "latest_price": float(last_price),
                    "price_change": float(price_change),
                    "discount_percentage": float(discount_percentage),
                    "price_volatility": float(price_volatility) if pd.notna(price_volatility) else 0.0,
                    "trend": trend,
                    "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }},
            upsert=True
        )
        updated_count += 1
        
    print(f"Price Analysis complete. Updated intelligence for {updated_count} products.")

if __name__ == "__main__":
    run_price_analysis()