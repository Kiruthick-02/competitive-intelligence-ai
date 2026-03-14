import pandas as pd

def analyze_price_trends(price_history: list):
    """
    Detects price drops, increases, and volatility over time.
    price_history format:[{"date": "2023-10-01", "price": 100}, ...]
    """
    if not price_history or len(price_history) < 2:
        return {"trend": "Stable", "change_percentage": 0}

    df = pd.DataFrame(price_history)
    df = df.sort_values(by="date")
    
    first_price = df['price'].iloc[0]
    last_price = df['price'].iloc[-1]
    
    change_pct = ((last_price - first_price) / first_price) * 100

    trend = "Stable"
    if change_pct <= -5:
        trend = "Price Drop Detected"
    elif change_pct >= 5:
        trend = "Price Increase Detected"

    return {
        "trend": trend,
        "change_percentage": round(change_pct, 2),
        "latest_price": last_price,
        "volatility": df['price'].std()
    }