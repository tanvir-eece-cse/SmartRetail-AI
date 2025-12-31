"""Model manager for loading and serving ML models."""

import os
from typing import Optional
import joblib
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ModelManager:
    """Manages ML model loading and inference."""
    
    def __init__(self):
        self.recommendation_model = None
        self.segmentation_model = None
        self.churn_model = None
        self.sentiment_model = None
        
    async def load_models(self):
        """Load all ML models."""
        logger.info("Loading ML models...")
        
        # Try to load models if they exist, otherwise use default behavior
        try:
            recommendation_path = os.path.join(settings.MODEL_PATH, "recommendation_model.joblib")
            if os.path.exists(recommendation_path):
                self.recommendation_model = joblib.load(recommendation_path)
                logger.info("Loaded recommendation model")
        except Exception as e:
            logger.warning(f"Could not load recommendation model: {e}")
        
        try:
            segmentation_path = os.path.join(settings.MODEL_PATH, "segmentation_model.joblib")
            if os.path.exists(segmentation_path):
                self.segmentation_model = joblib.load(segmentation_path)
                logger.info("Loaded segmentation model")
        except Exception as e:
            logger.warning(f"Could not load segmentation model: {e}")
        
        logger.info("Model loading complete")
    
    def get_user_recommendations(
        self,
        user_id: int,
        n_recommendations: int = 10
    ) -> list:
        """Get product recommendations for a user."""
        # Fallback to popular items if model not loaded
        if self.recommendation_model is None:
            return self._get_popular_products(n_recommendations)
        
        # Use model for recommendations
        try:
            recommendations = self.recommendation_model.recommend(
                user_id,
                n_recommendations
            )
            return recommendations
        except Exception:
            return self._get_popular_products(n_recommendations)
    
    def get_similar_products(
        self,
        product_id: int,
        n_similar: int = 10
    ) -> list:
        """Get similar products based on content features."""
        if self.recommendation_model is None:
            return []
        
        try:
            similar = self.recommendation_model.get_similar_items(
                product_id,
                n_similar
            )
            return similar
        except Exception:
            return []
    
    def segment_customer(self, rfm_data: dict) -> dict:
        """Segment a customer based on RFM metrics."""
        if self.segmentation_model is None:
            return self._rule_based_segmentation(rfm_data)
        
        try:
            segment = self.segmentation_model.predict([
                [rfm_data["recency"], rfm_data["frequency"], rfm_data["monetary"]]
            ])[0]
            return {"segment_id": int(segment), "segment_name": self._get_segment_name(segment)}
        except Exception:
            return self._rule_based_segmentation(rfm_data)
    
    def _get_popular_products(self, n: int) -> list:
        """Return placeholder popular products."""
        return [
            {"product_id": i, "score": 0.9 - (i * 0.05), "reason": "Popular product"}
            for i in range(1, n + 1)
        ]
    
    def _rule_based_segmentation(self, rfm_data: dict) -> dict:
        """Rule-based customer segmentation."""
        r, f, m = rfm_data["recency"], rfm_data["frequency"], rfm_data["monetary"]
        
        if r < 30 and f >= 10 and m >= 10000:
            return {"segment_id": 0, "segment_name": "Champions"}
        elif r < 60 and f >= 5:
            return {"segment_id": 1, "segment_name": "Loyal"}
        elif r < 30 and f < 3:
            return {"segment_id": 2, "segment_name": "New Customers"}
        elif r >= 90 and f >= 5:
            return {"segment_id": 3, "segment_name": "At Risk"}
        elif r >= 90:
            return {"segment_id": 4, "segment_name": "Hibernating"}
        else:
            return {"segment_id": 5, "segment_name": "Regular"}
    
    def _get_segment_name(self, segment_id: int) -> str:
        """Get segment name from ID."""
        segments = {
            0: "Champions",
            1: "Loyal",
            2: "New Customers",
            3: "At Risk",
            4: "Hibernating",
            5: "Regular"
        }
        return segments.get(segment_id, "Unknown")
