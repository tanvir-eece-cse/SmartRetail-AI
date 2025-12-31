"""
Recommendation Engine - Collaborative Filtering with Matrix Factorization
Author: Md. Tanvir Hossain
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from typing import List, Tuple, Optional
import joblib
import structlog

logger = structlog.get_logger(__name__)


class CollaborativeFilteringRecommender:
    """
    Hybrid recommendation engine combining:
    - Item-based collaborative filtering
    - Matrix factorization (SVD)
    - Content-based filtering
    """
    
    def __init__(
        self,
        n_factors: int = 50,
        n_neighbors: int = 20,
        min_interactions: int = 5
    ):
        self.n_factors = n_factors
        self.n_neighbors = n_neighbors
        self.min_interactions = min_interactions
        
        self.svd_model = None
        self.item_similarity_model = None
        self.user_item_matrix = None
        self.item_features = None
        
        self.user_id_map = {}
        self.product_id_map = {}
        self.reverse_user_map = {}
        self.reverse_product_map = {}
    
    def fit(
        self,
        interactions: pd.DataFrame,
        product_features: Optional[pd.DataFrame] = None
    ):
        """
        Train the recommendation model.
        
        Args:
            interactions: DataFrame with columns [user_id, product_id, rating/interaction_score]
            product_features: Optional DataFrame with product features for content-based filtering
        """
        logger.info("Training recommendation model", 
                   n_interactions=len(interactions))
        
        # Create ID mappings
        unique_users = interactions['user_id'].unique()
        unique_products = interactions['product_id'].unique()
        
        self.user_id_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.product_id_map = {pid: idx for idx, pid in enumerate(unique_products)}
        self.reverse_user_map = {idx: uid for uid, idx in self.user_id_map.items()}
        self.reverse_product_map = {idx: pid for pid, idx in self.product_id_map.items()}
        
        # Build user-item matrix
        rows = [self.user_id_map[u] for u in interactions['user_id']]
        cols = [self.product_id_map[p] for p in interactions['product_id']]
        values = interactions['rating'].values if 'rating' in interactions else np.ones(len(interactions))
        
        self.user_item_matrix = csr_matrix(
            (values, (rows, cols)),
            shape=(len(unique_users), len(unique_products))
        )
        
        # Train SVD model for matrix factorization
        self.svd_model = TruncatedSVD(
            n_components=min(self.n_factors, min(self.user_item_matrix.shape) - 1)
        )
        self.user_factors = self.svd_model.fit_transform(self.user_item_matrix)
        self.item_factors = self.svd_model.components_.T
        
        # Train item similarity model
        self.item_similarity_model = NearestNeighbors(
            n_neighbors=self.n_neighbors,
            metric='cosine',
            algorithm='brute'
        )
        self.item_similarity_model.fit(self.user_item_matrix.T.toarray())
        
        # Store product features for content-based filtering
        if product_features is not None:
            self.item_features = product_features
        
        logger.info("Model training complete",
                   n_users=len(unique_users),
                   n_products=len(unique_products))
    
    def recommend(
        self,
        user_id: int,
        n_recommendations: int = 10,
        exclude_purchased: bool = True
    ) -> List[dict]:
        """Get recommendations for a user using matrix factorization."""
        if user_id not in self.user_id_map:
            logger.warning("Unknown user, returning popular items", user_id=user_id)
            return self._get_popular_items(n_recommendations)
        
        user_idx = self.user_id_map[user_id]
        user_vector = self.user_factors[user_idx]
        
        # Compute scores for all items
        scores = np.dot(self.item_factors, user_vector)
        
        # Exclude already purchased items
        if exclude_purchased:
            purchased = self.user_item_matrix[user_idx].toarray().flatten()
            scores[purchased > 0] = -np.inf
        
        # Get top N items
        top_indices = np.argsort(scores)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            product_id = self.reverse_product_map[idx]
            recommendations.append({
                'product_id': int(product_id),
                'score': float(scores[idx]),
                'reason': 'Based on your preferences'
            })
        
        return recommendations
    
    def get_similar_items(
        self,
        product_id: int,
        n_similar: int = 10
    ) -> List[dict]:
        """Get similar products based on collaborative filtering."""
        if product_id not in self.product_id_map:
            return []
        
        product_idx = self.product_id_map[product_id]
        
        distances, indices = self.item_similarity_model.kneighbors(
            self.user_item_matrix.T[product_idx].toarray(),
            n_neighbors=n_similar + 1
        )
        
        similar_items = []
        for dist, idx in zip(distances[0][1:], indices[0][1:]):  # Skip the item itself
            similar_items.append({
                'product_id': int(self.reverse_product_map[idx]),
                'score': float(1 - dist),  # Convert distance to similarity
                'reason': 'Customers also bought'
            })
        
        return similar_items
    
    def _get_popular_items(self, n: int) -> List[dict]:
        """Return most popular items as fallback."""
        if self.user_item_matrix is None:
            return []
        
        popularity = np.array(self.user_item_matrix.sum(axis=0)).flatten()
        top_indices = np.argsort(popularity)[::-1][:n]
        
        return [
            {
                'product_id': int(self.reverse_product_map[idx]),
                'score': float(popularity[idx] / popularity.max()),
                'reason': 'Popular product'
            }
            for idx in top_indices
        ]
    
    def save(self, path: str):
        """Save the model to disk."""
        joblib.dump({
            'svd_model': self.svd_model,
            'item_similarity_model': self.item_similarity_model,
            'user_item_matrix': self.user_item_matrix,
            'user_factors': self.user_factors,
            'item_factors': self.item_factors,
            'user_id_map': self.user_id_map,
            'product_id_map': self.product_id_map,
            'reverse_user_map': self.reverse_user_map,
            'reverse_product_map': self.reverse_product_map
        }, path)
        logger.info("Model saved", path=path)
    
    @classmethod
    def load(cls, path: str) -> 'CollaborativeFilteringRecommender':
        """Load a model from disk."""
        data = joblib.load(path)
        model = cls()
        model.svd_model = data['svd_model']
        model.item_similarity_model = data['item_similarity_model']
        model.user_item_matrix = data['user_item_matrix']
        model.user_factors = data['user_factors']
        model.item_factors = data['item_factors']
        model.user_id_map = data['user_id_map']
        model.product_id_map = data['product_id_map']
        model.reverse_user_map = data['reverse_user_map']
        model.reverse_product_map = data['reverse_product_map']
        return model


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Generate sample data
    n_users = 1000
    n_products = 500
    n_interactions = 10000
    
    interactions = pd.DataFrame({
        'user_id': np.random.randint(1, n_users + 1, n_interactions),
        'product_id': np.random.randint(1, n_products + 1, n_interactions),
        'rating': np.random.uniform(1, 5, n_interactions)
    })
    
    # Train model
    recommender = CollaborativeFilteringRecommender(n_factors=30)
    recommender.fit(interactions)
    
    # Get recommendations
    user_id = 1
    recommendations = recommender.recommend(user_id, n_recommendations=5)
    print(f"\nRecommendations for user {user_id}:")
    for rec in recommendations:
        print(f"  Product {rec['product_id']}: score={rec['score']:.3f} - {rec['reason']}")
    
    # Get similar items
    product_id = 1
    similar = recommender.get_similar_items(product_id, n_similar=5)
    print(f"\nSimilar to product {product_id}:")
    for item in similar:
        print(f"  Product {item['product_id']}: similarity={item['score']:.3f}")
