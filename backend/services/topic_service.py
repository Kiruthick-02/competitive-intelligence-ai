from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from backend.utils.text_cleaner import clean_text

def extract_topics(reviews: list, num_topics=3, num_words=4):
    """
    Extracts complaint/discussion topics from a list of review texts using LDA.
    """
    cleaned_reviews = [clean_text(r) for r in reviews if r]
    if len(cleaned_reviews) < 5:
        return ["Not enough data for topic modeling"]

    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(cleaned_reviews)

    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)

    topics =[]
    feature_names = vectorizer.get_feature_names_out()
    
    for topic_idx, topic in enumerate(lda.components_):
        top_keywords =[feature_names[i] for i in topic.argsort()[:-num_words - 1:-1]]
        topics.append({"topic_id": topic_idx + 1, "keywords": top_keywords})
        
    return topics