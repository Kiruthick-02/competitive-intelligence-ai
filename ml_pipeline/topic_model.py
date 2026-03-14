import os
import re
from pymongo import MongoClient, UpdateOne
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text


def run_topic_modeling():

    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    print("Fetching ALL reviews...")

    reviews = list(db.reviews.find({}, {"reviewText": 1}))

    texts = []
    ids = []

    for r in reviews:
        cleaned = clean_text(r.get("reviewText", ""))

        if len(cleaned.split()) < 3:
            continue

        texts.append(cleaned)
        ids.append(r["_id"])

    print(f"Usable reviews: {len(texts)}")

    if len(texts) < 10:
        print("Not enough data.")
        return

    vectorizer = CountVectorizer(
        stop_words="english",
        max_df=0.9,
        min_df=5,
        ngram_range=(1,2),
        max_features=5000
    )

    dtm = vectorizer.fit_transform(texts)

    lda = LatentDirichletAllocation(
        n_components=5,
        random_state=42,
        learning_method="batch"
    )

    lda.fit(dtm)

    topic_distribution = lda.transform(dtm)

    operations = []

    for i, doc_id in enumerate(ids):

        dominant_topic = int(topic_distribution[i].argmax())

        operations.append(
            UpdateOne(
                {"_id": doc_id},
                {"$set": {"topic_id": dominant_topic + 1}}
            )
        )

        if len(operations) == 1000:
            db.reviews.bulk_write(operations)
            operations = []
            print(f"Updated {i+1} reviews...")

    if operations:
        db.reviews.bulk_write(operations)

    print("--------------------------------------------------")
    print("ALL Reviews Updated with Topics.")
    print(f"Total updated: {len(ids)}")
    print("--------------------------------------------------")

    client.close()


if __name__ == "__main__":
    run_topic_modeling()