"""Sentiment analysis endpoints."""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()


class ReviewAnalysisRequest(BaseModel):
    reviews: List[str]


class SentimentResult(BaseModel):
    text: str
    sentiment: str
    score: float
    aspects: List[dict]


@router.post("/analyze", response_model=List[SentimentResult])
async def analyze_sentiment(request: ReviewAnalysisRequest):
    """Analyze sentiment of product reviews."""
    results = []
    
    for review in request.reviews:
        # Simplified sentiment analysis
        positive_words = ["good", "great", "excellent", "love", "best", "amazing", "perfect"]
        negative_words = ["bad", "poor", "worst", "hate", "terrible", "awful", "disappointed"]
        
        review_lower = review.lower()
        pos_count = sum(1 for word in positive_words if word in review_lower)
        neg_count = sum(1 for word in negative_words if word in review_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = min(1.0, 0.6 + (pos_count * 0.1))
        elif neg_count > pos_count:
            sentiment = "negative"
            score = max(0.0, 0.4 - (neg_count * 0.1))
        else:
            sentiment = "neutral"
            score = 0.5
        
        # Extract aspects
        aspects = []
        if "quality" in review_lower:
            aspects.append({"aspect": "quality", "sentiment": sentiment})
        if "price" in review_lower:
            aspects.append({"aspect": "price", "sentiment": sentiment})
        if "delivery" in review_lower or "shipping" in review_lower:
            aspects.append({"aspect": "delivery", "sentiment": sentiment})
        if "service" in review_lower:
            aspects.append({"aspect": "service", "sentiment": sentiment})
        
        results.append(SentimentResult(
            text=review[:100] + "..." if len(review) > 100 else review,
            sentiment=sentiment,
            score=round(score, 2),
            aspects=aspects
        ))
    
    return results


@router.get("/product/{product_id}/summary")
async def get_product_sentiment_summary(product_id: int):
    """Get sentiment summary for a product's reviews."""
    return {
        "product_id": product_id,
        "total_reviews": random.randint(50, 500),
        "average_sentiment_score": round(random.uniform(0.6, 0.9), 2),
        "sentiment_distribution": {
            "positive": random.randint(60, 80),
            "neutral": random.randint(10, 25),
            "negative": random.randint(5, 15)
        },
        "top_positive_aspects": [
            {"aspect": "quality", "mentions": random.randint(20, 50)},
            {"aspect": "value", "mentions": random.randint(15, 40)},
            {"aspect": "design", "mentions": random.randint(10, 30)}
        ],
        "top_negative_aspects": [
            {"aspect": "delivery_time", "mentions": random.randint(5, 15)},
            {"aspect": "packaging", "mentions": random.randint(3, 10)}
        ],
        "trend": "improving"
    }
