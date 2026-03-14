import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from ml_pipeline.data_preprocessing import clean_reviews, clean_products, clean_prices

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")

def get_mongo_client():
    client = MongoClient(MONGO_URI)
    print(f"Connected to MongoDB: {DATABASE_NAME}")
    return client[DATABASE_NAME]

def load_csv_to_mongo(file_path: str, collection_name: str, clean_func, db, limit_rows=None):
    """
    Reads a CSV, cleans it, and uploads it to a MongoDB collection.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found -> {file_path}")
        return

    try:
        # Read CSV with nrows limit to save RAM and Database space
        print(f"\nReading {file_path}...")
        if limit_rows:
            print(f"Limiting to first {limit_rows} rows...")
            df = pd.read_csv(file_path, low_memory=False, nrows=limit_rows)
        else:
            df = pd.read_csv(file_path, low_memory=False)
        
        # Clean Data
        df_cleaned = clean_func(df)
        
        # Convert to dictionary format for MongoDB
        records = df_cleaned.to_dict(orient='records')
        
        if records:
            # IMPORTANT: Use .drop() instead of delete_many() to instantly free up disk space in Atlas
            db[collection_name].drop()
            print(f"Dropped existing '{collection_name}' collection to free up space.")
            
            # Insert new data
            db[collection_name].insert_many(records)
            print(f"Successfully inserted {len(records)} records into '{collection_name}'.")
        else:
            print(f"No valid records found to insert for {collection_name}.")
            
    except Exception as e:
        print(f"Failed to process {file_path}. Error: {e}")

if __name__ == "__main__":
    db = get_mongo_client()
    
    # Define file paths
    REVIEWS_CSV = os.path.join("datasets", "reviews.csv")
    PRODUCTS_CSV = os.path.join("datasets", "products.csv")
    PRICES_CSV = os.path.join("datasets", "prices.csv")
    
    # Execute the pipeline
    print("\n--- Starting Data Ingestion Pipeline ---")
    
    # Limit products to 2 Lakhs (200,000) so it fits in the 512MB Free Tier!
    load_csv_to_mongo(PRODUCTS_CSV, "products", clean_products, db, limit_rows=200000)
    
    # Reviews and Prices are small enough, so we load all of them
    load_csv_to_mongo(REVIEWS_CSV, "reviews", clean_reviews, db)
    load_csv_to_mongo(PRICES_CSV, "prices", clean_prices, db)
    
    print("\n--- Data Ingestion Complete ---")
    
    # Create indexes for faster queries
    print("Building database indexes...")
    db.reviews.create_index("asin")
    db.products.create_index("asin")
    db.prices.create_index("asins")
    print("Indexes built successfully!")