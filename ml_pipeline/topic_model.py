import os
import re
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "competitive_intelligence")

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def run_topic_modeling():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    print("Starting Topic Modeling (LDA)...")
    
    # Get all unique products that have reviews
    unique_asins = db.reviews.distinct("asin")
    print(f"Found {len(unique_asins)} products to analyze.")
    
    for asin in unique_asins:
        # Fetch only Negative or Neutral reviews for complaint extraction
        reviews = list(db.reviews.find({"asin": asin, "sentiment": {"$in": ["Negative", "Neutral"]}}))
        
        cleaned_reviews =[clean_text(r.get("reviewText", "")) for r in reviews if r.get("reviewText")]
        cleaned_reviews =[r for r in cleaned_reviews if len(r.split()) > 3] # Keep meaningful sentences
        
        if len(cleaned_reviews) < 5:
            # Not enough data for LDA
            continue
            
        try:
            vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
            dtm = vectorizer.fit_transform(cleaned_reviews)
            
            # Extract 3 main topics
            lda = LatentDirichletAllocation(n_components=3, random_state=42)
            lda.fit(dtm)
            
            topics =[]
            feature_names = vectorizer.get_feature_names_out()
            for topic_idx, topic in enumerate(lda.components_):
                # Get top 5 keywords per topic
                top_keywords = [feature_names[i] for i in topic.argsort()[:-5 - 1:-1]]
                topics.append({"topic_id": topic_idx + 1, "keywords": top_keywords})
            
            # Save the topics into the insights collection
            db.insights.update_one(
                {"asin": asin},
                {"$set": {"asin": asin, "complaint_topics": topics}},
                upsert=True
            )
            print(f"Processed topics for ASIN: {asin}")
            
        except Exception as e:
            print(f"Skipping ASIN {asin} due to error: {e}")

    print("Topic Modeling Complete!")

if __name__ == "__main__":
    run_topic_modeling()