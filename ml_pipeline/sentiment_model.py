import os
import time
import warnings
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from transformers import pipeline
from dotenv import load_dotenv

# Suppress annoying deprecation and library warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")

def run_sentiment_analysis_batch():
    client = None
    db = None
    
    print("Connecting to MongoDB...")
    # Retry logic for DNS/Network instability
    for attempt in range(3):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client[DATABASE_NAME]
            # Verify connection
            db.command('ping')
            print("Successfully connected to MongoDB.")
            break
        except PyMongoError as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(3)
            else:
                print("Could not connect to database. Please check your internet/DNS settings.")
                return

    print("Loading BERT Sentiment Model (distilbert-base-uncased-finetuned-sst-2-english)...")
    try:
        sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    except Exception as e:
        print(f"Failed to load BERT model: {e}")
        return

    # Find reviews that do not have sentiment scores yet
    unprocessed_reviews = list(db.reviews.find({"sentiment": {"$exists": False}}))
    
    if not unprocessed_reviews:
        print("All reviews are already processed!")
        return

    print(f"Processing {len(unprocessed_reviews)} reviews for sentiment...")
    
    count = 0
    for review in unprocessed_reviews:
        text = review.get("reviewText", "")
        
        if not isinstance(text, str) or not text.strip():
            sentiment, score = "Neutral", 0.5
        else:
            try:
                # BERT has a 512 token limit; we truncate to prevent errors
                result = sentiment_pipeline(text[:512])[0]
                label = result['label']
                score = result['score']
                
                # Neutral threshold logic
                if score < 0.60:
                    sentiment = "Neutral"
                else:
                    sentiment = "Positive" if label == "POSITIVE" else "Negative"
            except Exception as e:
                sentiment, score = "Neutral", 0.5

        # Update the specific document
        db.reviews.update_one(
            {"_id": review["_id"]},
            {"$set": {"sentiment": sentiment, "sentiment_score": float(score)}}
        )
        count += 1
        if count % 100 == 0:
            print(f"Processed {count}/{len(unprocessed_reviews)} reviews...")
        
    print(f"Successfully updated {count} reviews with sentiment analysis.")

if __name__ == "__main__":
    run_sentiment_analysis_batch()