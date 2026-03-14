from transformers import pipeline

# Load BERT model on startup to save latency
print("Loading Sentiment Analysis Model (BERT)...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text: str):
    """
    Returns Positive, Negative, or Neutral based on BERT score.
    """
    if not text.strip():
        return "Neutral"
    
    # Truncate text to 512 tokens to avoid BERT errors
    truncated_text = text[:512]
    result = sentiment_pipeline(truncated_text)[0]
    
    label = result['label']
    score = result['score']
    
    # Adjusting strictly positive/negative to include neutral for low confidence
    if score < 0.60:
        return "Neutral"
    return "Positive" if label == "POSITIVE" else "Negative"