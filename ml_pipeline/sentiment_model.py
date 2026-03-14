import os
import time
import warnings
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
from transformers import pipeline
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")


def run_sentiment_analysis_batch():

    print("Connecting to MongoDB...")

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        db.command("ping")
        print("Successfully connected.")
    except PyMongoError as e:
        print("Database connection failed:", e)
        return

    print("Loading BERT model...")

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    # 🔥 Get ALL reviews (not just unprocessed)
    reviews = list(db.reviews.find({}, {"reviewText": 1}))

    if not reviews:
        print("No reviews found.")
        return

    print(f"Total reviews found: {len(reviews)}")

    batch_size = 32  # Efficient for BERT
    operations = []
    processed = 0

    for i in range(0, len(reviews), batch_size):

        batch = reviews[i:i + batch_size]
        texts = []

        for r in batch:
            text = r.get("reviewText", "")

            if isinstance(text, str) and text.strip():
                texts.append(text[:512])  # BERT limit
            else:
                texts.append("")

        try:
            results = sentiment_pipeline(texts)

        except Exception:
            continue

        for r, result in zip(batch, results):

            label = result["label"]
            score = float(result["score"])

            # Neutral threshold logic
            if score < 0.60:
                sentiment = "Neutral"
            else:
                sentiment = "Positive" if label == "POSITIVE" else "Negative"

            operations.append(
                UpdateOne(
                    {"_id": r["_id"]},
                    {
                        "$set": {
                            "sentiment": sentiment,
                            "sentiment_score": score
                        }
                    }
                )
            )

            processed += 1

        # 🔥 Bulk write every 1000 updates
        if len(operations) >= 1000:
            db.reviews.bulk_write(operations)
            operations = []
            print(f"Processed {processed}/{len(reviews)} reviews...")

    # Final write
    if operations:
        db.reviews.bulk_write(operations)

    print("--------------------------------------------------")
    print("Sentiment Analysis Complete.")
    print(f"Total reviews updated: {processed}")
    print("--------------------------------------------------")

    client.close()


if __name__ == "__main__":
    run_sentiment_analysis_batch()