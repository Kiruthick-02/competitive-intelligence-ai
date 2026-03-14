from fastapi import APIRouter, HTTPException
from backend.database.mongodb import get_db
from backend.services.sentiment_service import analyze_sentiment

router = APIRouter()

@router.get("/{asin}")
async def get_reviews(asin: str):
    db = get_db()
    cursor = db.reviews.find({"asin": asin}).limit(100)
    reviews = await cursor.to_list(length=100)
    
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this ASIN")

    # Serialize ObjectId
    for rev in reviews:
        rev["_id"] = str(rev["_id"])
        
    return {"asin": asin, "reviews": reviews}

@router.post("/analyze/{asin}")
async def process_reviews_sentiment(asin: str):
    db = get_db()
    cursor = db.reviews.find({"asin": asin})
    reviews = await cursor.to_list(length=500)
    
    updated_count = 0
    for rev in reviews:
        if "sentiment" not in rev:
            sentiment = analyze_sentiment(rev.get("reviewText", ""))
            await db.reviews.update_one(
                {"_id": rev["_id"]},
                {"$set": {"sentiment": sentiment}}
            )
            updated_count += 1
            
    return {"message": f"Processed sentiment for {updated_count} reviews."}