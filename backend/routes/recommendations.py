from fastapi import APIRouter, HTTPException
from backend.database.mongodb import get_db
from backend.services.topic_service import extract_topics
from backend.services.price_analysis import analyze_price_trends
from backend.services.intelligence_engine import generate_strategic_recommendation

# THIS LINE WAS MISSING OR DELETED:
router = APIRouter()

@router.get("/generate/{asin}")
async def get_agent_recommendation(asin: str):
    db = get_db()
    
    # 1. Fetch Product
    product = await db.products.find_one({"asin": asin})
    # We don't 404 anymore if product is missing, we just use the ASIN as title
    product_title = product.get("title", asin) if product else asin

    # 2. Fetch Reviews
    cursor = db.reviews.find({"asin": asin})
    reviews = await cursor.to_list(length=1000)
    
    # Handle case with 0 reviews (like B07GDLCQXV)
    if not reviews:
        negative_pct = 0
        topics_data = []
        top_complaints = ["No review data available"]
    else:
        total_reviews = len(reviews)
        negative_reviews = [r for r in reviews if r.get("sentiment") == "Negative"]
        negative_pct = (len(negative_reviews) / total_reviews) * 100
        neg_texts = [r.get("reviewText", "") for r in negative_reviews]
        
        # Call topic service safely
        try:
            topics_data = extract_topics(neg_texts)
            top_complaints = [kw for topic in topics_data if isinstance(topic, dict) for kw in topic.get('keywords', [])]
        except:
            topics_data = []
            top_complaints = ["Error extracting topics"]

    # 3. Fetch Pricing Trends
    prices_cursor = db.prices.find({"asins": {"$regex": asin, "$options": "i"}})
    prices_list = await prices_cursor.to_list(length=50)
    
    formatted_prices = []
    for p in prices_list:
        if "prices" in p:
            p_info = p["prices"]
            # Handle if dateSeen is a list or a comma-string
            d_val = p_info.get("dateSeen")
            clean_date = d_val[0] if isinstance(d_val, list) else d_val.split(',')[0] if d_val else None
            if clean_date:
                formatted_prices.append({"date": clean_date, "price": p_info.get("amountMax", 0)})

    price_trend = analyze_price_trends(formatted_prices)

    # 4. Generate AI Strategy
    ai_strategy = generate_strategic_recommendation(
        product_name=product_title,
        negative_pct=negative_pct,
        top_complaints=list(set(top_complaints))[:5],
        price_trend=price_trend
    )

    result = {
        "asin": asin,
        "product_title": product_title,
        "metrics": {
            "total_reviews": len(reviews),
            "negative_sentiment_percentage": round(negative_pct, 2),
            "top_complaint_topics": topics_data,
            "price_intelligence": price_trend
        },
        "ai_recommendation": ai_strategy
    }

    # Save insight
    await db.insights.update_one({"asin": asin}, {"$set": result}, upsert=True)
    return result