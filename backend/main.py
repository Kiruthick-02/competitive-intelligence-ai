from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.mongodb import connect_to_mongo, close_mongo_connection

# Import ALL your routes
from backend.routes import reviews, recommendations, products, prices

app = FastAPI(
    title="Competitive Intelligence AI API",
    description="Agentic layer for e-commerce cross-platform intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    close_mongo_connection()

# --- REGISTER ALL ROUTERS HERE ---
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(recommendations.router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(prices.router, prefix="/api/prices", tags=["Prices"])

@app.get("/")
def health_check():
    return {"status": "Running", "service": "Competitive Intelligence AI Backend"}