from fastapi import APIRouter
from backend.database.mongodb import get_db

router = APIRouter()

@router.get("/{asin}")
async def get_price_history(asin: str):
    db = get_db()
    # Search using regex because ASINs in this dataset are often comma-separated strings
    cursor = db.prices.find({"asins": {"$regex": asin, "$options": "i"}})
    prices_data = await cursor.to_list(length=100)
    
    if not prices_data:
        return {"asin": asin, "total_records": 0, "price_history": []}

    history = []
    for item in prices_data:
        p_data = item.get("prices")
        if not p_data: continue
            
        if isinstance(p_data, list):
            for p_event in p_data:
                history.append(_format_price_event(p_event, item.get("brand", "Retailer")))
        else:
            history.append(_format_price_event(p_data, item.get("brand", "Retailer")))

    # Filter out records with no dates and sort chronologically
    history = [h for h in history if h['date']]
    history = sorted(history, key=lambda x: x["date"])

    return {"asin": asin, "total_records": len(history), "price_history": history}

def _format_price_event(price_obj: dict, default_brand: str):
    raw_date = price_obj.get("dateSeen", "")
    
    # Clean up messy date strings (e.g., "2018-05-26T00:00:00Z,2018-05-27...")
    if isinstance(raw_date, list): raw_date = raw_date[0]
    clean_date = None
    if isinstance(raw_date, str) and raw_date:
        # Take the first date in the string, then strip the time 'T' part
        clean_date = raw_date.split(',')[0].split('T')[0]
    
    return {
        "date": clean_date,
        "price": float(price_obj.get("amountMax", 0)), # 'price' is used by PriceChart.jsx
        "merchant": price_obj.get("merchant", default_brand)
    }