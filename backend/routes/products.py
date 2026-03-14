from fastapi import APIRouter, HTTPException, Query
from backend.database.mongodb import get_db

router = APIRouter()

@router.get("/search")
async def search_products(q: str = Query(..., min_length=2)):
    db = get_db()
    
    # 1. Find up to 50 products matching the search query
    cursor = db.products.find({"title": {"$regex": q, "$options": "i"}}).limit(50)
    matches = await cursor.to_list(length=50)
    
    if not matches:
        raise HTTPException(status_code=404, detail="No products found")

    # 2. Optimization: Find a match that actually HAS reviews
    # This prevents the UI from showing empty charts
    for product in matches:
        review_count = await db.reviews.count_documents({"asin": product["asin"]})
        if review_count > 0:
            product["_id"] = str(product["_id"])
            # Return this as a list of one successful match
            return [product]

    # 3. Fallback: If no matches have reviews, just return the first one found
    matches[0]["_id"] = str(matches[0]["_id"])
    return [matches[0]]

@router.get("/{asin}")
async def get_product_by_asin(asin: str):
    db = get_db()
    product = await db.products.find_one({"asin": asin})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product["_id"] = str(product["_id"])
    return product