"""Tests for recommendation engine."""

import pytest
import numpy as np
import pandas as pd

from app.models.recommendation_engine import CollaborativeFilteringRecommender


class TestCollaborativeFilteringRecommender:
    """Tests for the collaborative filtering recommender."""
    
    @pytest.fixture
    def sample_interactions(self):
        """Create sample interaction data."""
        np.random.seed(42)
        return pd.DataFrame({
            'user_id': np.random.randint(1, 101, 500),
            'product_id': np.random.randint(1, 51, 500),
            'rating': np.random.uniform(1, 5, 500)
        })
    
    @pytest.fixture
    def trained_recommender(self, sample_interactions):
        """Create and train a recommender."""
        recommender = CollaborativeFilteringRecommender(n_factors=10)
        recommender.fit(sample_interactions)
        return recommender
    
    def test_fit(self, sample_interactions):
        """Test model training."""
        recommender = CollaborativeFilteringRecommender(n_factors=10)
        recommender.fit(sample_interactions)
        
        assert recommender.user_item_matrix is not None
        assert recommender.svd_model is not None
        assert recommender.item_similarity_model is not None
    
    def test_recommend_known_user(self, trained_recommender):
        """Test recommendations for a known user."""
        recommendations = trained_recommender.recommend(1, n_recommendations=5)
        
        assert len(recommendations) == 5
        assert all('product_id' in r for r in recommendations)
        assert all('score' in r for r in recommendations)
    
    def test_recommend_unknown_user(self, trained_recommender):
        """Test recommendations for an unknown user."""
        recommendations = trained_recommender.recommend(99999, n_recommendations=5)
        
        # Should return popular items for unknown users
        assert len(recommendations) == 5
    
    def test_similar_items(self, trained_recommender):
        """Test similar items retrieval."""
        similar = trained_recommender.get_similar_items(1, n_similar=5)
        
        assert len(similar) <= 5
        if similar:
            assert all('product_id' in item for item in similar)
            assert all('score' in item for item in similar)


class TestCustomerSegmentation:
    """Tests for customer segmentation."""
    
    @pytest.fixture
    def sample_rfm_data(self):
        """Create sample RFM data."""
        np.random.seed(42)
        return pd.DataFrame({
            'customer_id': range(1, 101),
            'recency': np.random.exponential(60, 100).astype(int),
            'frequency': np.random.poisson(5, 100) + 1,
            'monetary': np.random.exponential(5000, 100)
        })
    
    def test_segmentation(self, sample_rfm_data):
        """Test customer segmentation."""
        from app.models.customer_segmentation import CustomerSegmentation
        
        segmentation = CustomerSegmentation(n_clusters=4)
        segmentation.fit(sample_rfm_data)
        
        assert segmentation.kmeans is not None
        assert len(segmentation.segment_profiles) == 4
    
    def test_predict_segment(self, sample_rfm_data):
        """Test segment prediction."""
        from app.models.customer_segmentation import CustomerSegmentation
        
        segmentation = CustomerSegmentation(n_clusters=4)
        segmentation.fit(sample_rfm_data)
        
        result = segmentation.segment_customer({
            'recency': 10,
            'frequency': 15,
            'monetary': 25000
        })
        
        assert 'segment_id' in result
        assert 'segment_name' in result
        assert result['segment_id'] in range(4)


class TestDemandForecaster:
    """Tests for demand forecaster."""
    
    @pytest.fixture
    def sample_sales_data(self):
        """Create sample sales data."""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        return pd.DataFrame({
            'date': dates,
            'quantity': np.random.poisson(100, 90)
        })
    
    def test_fit_and_forecast(self, sample_sales_data):
        """Test forecaster training and prediction."""
        from app.models.demand_forecaster import DemandForecaster
        
        forecaster = DemandForecaster(horizon_days=7)
        forecaster.fit(sample_sales_data)
        
        forecast = forecaster.forecast()
        
        assert len(forecast) == 7
        assert all('predicted_demand' in f for f in forecast)
        assert all('lower_bound' in f for f in forecast)
        assert all('upper_bound' in f for f in forecast)
    
    def test_inventory_recommendation(self, sample_sales_data):
        """Test inventory recommendation."""
        from app.models.demand_forecaster import DemandForecaster
        
        forecaster = DemandForecaster()
        forecaster.fit(sample_sales_data)
        
        recommendation = forecaster.get_inventory_recommendation(
            current_stock=500,
            lead_time_days=5
        )
        
        assert 'urgency' in recommendation
        assert 'recommended_order' in recommendation
        assert recommendation['current_stock'] == 500
