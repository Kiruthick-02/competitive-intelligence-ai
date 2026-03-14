from backend.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

def generate_strategic_recommendation(product_name: str, negative_pct: float, top_complaints: list, price_trend: dict):
    """
    Connects signals and generates strategy. Falls back to Rule-Engine if OpenAI quota is exceeded.
    """
    trigger_alert = negative_pct > 25.0 or price_trend.get("change_percentage", 0) <= -10.0
    strategy = ""

    # --- 1. Attempt Real AI (OpenAI) ---
    api_key = settings.OPENAI_API_KEY
    if api_key and not api_key.startswith("sk-proj-XXXX"):
        try:
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=api_key)
            prompt = PromptTemplate(
                input_variables=["product", "negative_pct", "complaints", "price_change"],
                template="Act as an E-commerce Strategist. Product: {product}. Negative sentiment: {negative_pct}%. Complaints: {complaints}. Price changed: {price_change}%. Provide a 3-bullet point strategy."
            )
            chain = prompt | llm
            response = chain.invoke({
                "product": product_name, "negative_pct": negative_pct,
                "complaints": ", ".join(top_complaints), "price_change": price_trend.get("change_percentage", 0)
            })
            return {"alert_triggered": trigger_alert, "strategy_recommendation": response.content}
        except Exception as e:
            print(f"AI Quota/Error: {e} - Switching to Rule-Based Intelligence...")

    # --- 2. SMART RULE-ENGINE (Simulated AI using real data) ---
    # We build the strategy based on your actual database results
    
    # Bullet 1: Sentiment Strategy
    if negative_pct > 30:
        bullet_1 = f"🚨 URGENT QUALITY PIVOT: Negative sentiment is critical at {negative_pct}%. You must address '{top_complaints[0] if top_complaints else 'product reliability'}' immediately to prevent ranking collapse."
    elif negative_pct > 15:
        bullet_1 = f"⚠️ OPTIMIZATION REQUIRED: Address minor complaints regarding '{top_complaints[0] if top_complaints else 'usability'}' to stay ahead of competitors."
    else:
        bullet_1 = "✅ SENTIMENT LEADERSHIP: Sentiment is healthy. Leverage this as a 'High Quality' USP in your Sponsored Product ads."

    # Bullet 2: Pricing Strategy
    price_change = price_trend.get("change_percentage", 0)
    if price_change <= -10:
        bullet_2 = f"📉 PRICE WAR DETECTED: Competitors dropped prices by {abs(price_change)}%. Do not match price; instead, offer a 'Buy 2, Get 10% Off' bundle to protect your margins."
    elif price_change >= 10:
        bullet_2 = f"💰 PROFIT OPPORTUNITY: Competitors increased prices by {price_change}%. You have a {price_change}% pricing gap advantage. Maintain your current price to steal their traffic."
    else:
        bullet_2 = "📊 STABLE MARKET: Competitor pricing is stable. Focus on SEO keyword expansion rather than price adjustments."

    # Bullet 3: Actionable Move
    if trigger_alert:
        bullet_3 = "🎯 DEFENSIVE MOVE: Pause aggressive ad spend on low-rated variations and redirect budget to your highest-rated 'Hero' product."
    else:
        bullet_3 = "🚀 GROWTH MOVE: Market conditions are optimal. Launch a 15% 'Limited Time Deal' to trigger Amazon's 'Best Seller' badge."

    strategy = f"1. {bullet_1}\n\n2. {bullet_2}\n\n3. {bullet_3}"

    return {
        "alert_triggered": trigger_alert,
        "strategy_recommendation": strategy
    }