import pandas as pd
import numpy as np

def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Customer Reviews Dataset.
    """
    print("Cleaning Reviews Data...")
    
    # Drop rows where essential fields are missing
    df = df.dropna(subset=['asin', 'reviewText'])
    
    # Remove exact duplicates
    df = df.drop_duplicates()
    
    # Fill missing summary or reviewerName with placeholders
    df['summary'] = df['summary'].fillna("No Summary")
    df['reviewerName'] = df['reviewerName'].fillna("Anonymous")
    
    # Ensure 'overall' (rating) is numeric
    df['overall'] = pd.to_numeric(df['overall'], errors='coerce').fillna(3.0)
    
    # Convert unix time to standard datetime string
    if 'unixReviewTime' in df.columns:
        df['reviewDate'] = pd.to_datetime(df['unixReviewTime'], unit='s').dt.strftime('%Y-%m-%d')
        
    return df

def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Product Metadata Dataset.
    """
    print("Cleaning Products Data...")
    
    # Drop rows without ASIN or Title
    df = df.dropna(subset=['asin', 'title'])
    df = df.drop_duplicates(subset=['asin'])
    
    # Clean price column (remove '$' or other characters if present)
    if 'price' in df.columns and df['price'].dtype == object:
        df['price'] = df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
        
    # Ensure stars and reviews are numeric
    df['stars'] = pd.to_numeric(df['stars'], errors='coerce').fillna(0.0)
    df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0)
    
    # Fill missing categories
    df['category_id'] = df['category_id'].fillna("Unknown")
    df['isBestSeller'] = df['isBestSeller'].fillna(False)
    
    return df

def clean_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Competitor Price Dataset.
    """
    print("Cleaning Prices Data...")
    
    # Ensure asins exist
    df = df.dropna(subset=['asins'])
    
    # Ensure price max and min are numeric
    df['prices.amountMax'] = pd.to_numeric(df['prices.amountMax'], errors='coerce').fillna(0.0)
    df['prices.amountMin'] = pd.to_numeric(df['prices.amountMin'], errors='coerce').fillna(0.0)
    
    # Re-structure flat CSV columns into nested dicts for the backend to consume easily
    # e.g., mapping flat 'prices.amountMax' to a nested 'prices' object
    def build_nested_price(row):
        return {
            "amountMax": row.get('prices.amountMax'),
            "amountMin": row.get('prices.amountMin'),
            "dateSeen": row.get('prices.dateSeen'),
            "merchant": row.get('prices.merchant', 'Unknown')
        }
        
    df['prices'] = df.apply(build_nested_price, axis=1)
    
    # Keep only the necessary columns
    columns_to_keep = ['asins', 'brand', 'categories', 'prices']
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    
    return df[existing_columns]