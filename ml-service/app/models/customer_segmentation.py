"""
Customer Segmentation using RFM Analysis and K-Means Clustering
Author: Md. Tanvir Hossain
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from typing import Dict, List, Tuple
import joblib
import structlog

logger = structlog.get_logger(__name__)


class CustomerSegmentation:
    """
    RFM-based customer segmentation with K-Means clustering.
    
    Segments customers based on:
    - Recency: How recently a customer made a purchase
    - Frequency: How often they purchase
    - Monetary: How much they spend
    """
    
    SEGMENT_NAMES = {
        0: "Champions",
        1: "Loyal",
        2: "New Customers",
        3: "At Risk",
        4: "Hibernating",
        5: "Regular"
    }
    
    def __init__(self, n_clusters: int = 6):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.cluster_centers_original = None
        self.segment_profiles = None
    
    def compute_rfm(
        self,
        transactions: pd.DataFrame,
        customer_id_col: str = 'customer_id',
        date_col: str = 'order_date',
        amount_col: str = 'total_amount',
        analysis_date: pd.Timestamp = None
    ) -> pd.DataFrame:
        """
        Compute RFM metrics from transaction data.
        
        Args:
            transactions: DataFrame with customer transactions
            customer_id_col: Column name for customer ID
            date_col: Column name for transaction date
            amount_col: Column name for transaction amount
            analysis_date: Reference date for recency calculation
        """
        if analysis_date is None:
            analysis_date = pd.Timestamp.now()
        
        transactions[date_col] = pd.to_datetime(transactions[date_col])
        
        rfm = transactions.groupby(customer_id_col).agg({
            date_col: lambda x: (analysis_date - x.max()).days,  # Recency
            customer_id_col: 'count',  # Frequency
            amount_col: 'sum'  # Monetary
        })
        
        rfm.columns = ['recency', 'frequency', 'monetary']
        rfm = rfm.reset_index()
        
        logger.info("Computed RFM metrics", n_customers=len(rfm))
        
        return rfm
    
    def fit(self, rfm_data: pd.DataFrame) -> 'CustomerSegmentation':
        """
        Train the segmentation model on RFM data.
        
        Args:
            rfm_data: DataFrame with columns [customer_id, recency, frequency, monetary]
        """
        features = rfm_data[['recency', 'frequency', 'monetary']].values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Find optimal number of clusters using silhouette score
        if self.n_clusters is None:
            best_score = -1
            best_k = 2
            
            for k in range(2, 11):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(features_scaled)
                score = silhouette_score(features_scaled, labels)
                
                if score > best_score:
                    best_score = score
                    best_k = k
            
            self.n_clusters = best_k
            logger.info("Optimal clusters found", n_clusters=best_k, silhouette=best_score)
        
        # Train K-Means
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10
        )
        labels = self.kmeans.fit_predict(features_scaled)
        
        # Store original scale cluster centers
        self.cluster_centers_original = self.scaler.inverse_transform(
            self.kmeans.cluster_centers_
        )
        
        # Create segment profiles
        self._create_segment_profiles(rfm_data, labels)
        
        logger.info("Segmentation model trained", 
                   n_clusters=self.n_clusters,
                   n_customers=len(rfm_data))
        
        return self
    
    def _create_segment_profiles(
        self,
        rfm_data: pd.DataFrame,
        labels: np.ndarray
    ):
        """Create profiles for each segment."""
        rfm_data = rfm_data.copy()
        rfm_data['segment'] = labels
        
        self.segment_profiles = {}
        
        for segment_id in range(self.n_clusters):
            segment_data = rfm_data[rfm_data['segment'] == segment_id]
            
            self.segment_profiles[segment_id] = {
                'name': self._assign_segment_name(
                    segment_data['recency'].mean(),
                    segment_data['frequency'].mean(),
                    segment_data['monetary'].mean()
                ),
                'size': len(segment_data),
                'percentage': len(segment_data) / len(rfm_data) * 100,
                'avg_recency': segment_data['recency'].mean(),
                'avg_frequency': segment_data['frequency'].mean(),
                'avg_monetary': segment_data['monetary'].mean(),
            }
    
    def _assign_segment_name(
        self,
        avg_recency: float,
        avg_frequency: float,
        avg_monetary: float
    ) -> str:
        """Assign meaningful name based on RFM characteristics."""
        if avg_recency < 30 and avg_frequency >= 10 and avg_monetary >= 10000:
            return "Champions"
        elif avg_recency < 60 and avg_frequency >= 5:
            return "Loyal"
        elif avg_recency < 30 and avg_frequency < 3:
            return "New Customers"
        elif avg_recency >= 90 and avg_frequency >= 5:
            return "At Risk"
        elif avg_recency >= 90:
            return "Hibernating"
        else:
            return "Regular"
    
    def predict(self, rfm_values: np.ndarray) -> np.ndarray:
        """
        Predict segment for new customers.
        
        Args:
            rfm_values: Array of shape (n_samples, 3) with [recency, frequency, monetary]
        """
        if self.kmeans is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        scaled = self.scaler.transform(rfm_values)
        return self.kmeans.predict(scaled)
    
    def segment_customer(self, rfm_data: Dict) -> Dict:
        """
        Segment a single customer.
        
        Args:
            rfm_data: Dict with keys 'recency', 'frequency', 'monetary'
        """
        values = np.array([[
            rfm_data['recency'],
            rfm_data['frequency'],
            rfm_data['monetary']
        ]])
        
        segment_id = self.predict(values)[0]
        
        return {
            'segment_id': int(segment_id),
            'segment_name': self.segment_profiles[segment_id]['name'],
            'segment_profile': self.segment_profiles[segment_id]
        }
    
    def get_segment_recommendations(self, segment_id: int) -> Dict:
        """Get marketing recommendations for a segment."""
        recommendations = {
            "Champions": {
                "actions": [
                    "Reward with exclusive offers",
                    "Early access to new products",
                    "Referral program incentives"
                ],
                "channels": ["Email", "Push notifications", "VIP events"]
            },
            "Loyal": {
                "actions": [
                    "Upsell higher value products",
                    "Loyalty program enrollment",
                    "Personalized recommendations"
                ],
                "channels": ["Email", "SMS", "In-app"]
            },
            "New Customers": {
                "actions": [
                    "Welcome email series",
                    "First purchase discount",
                    "Product education content"
                ],
                "channels": ["Email", "Onboarding guides"]
            },
            "At Risk": {
                "actions": [
                    "Win-back campaigns",
                    "Special discounts",
                    "Feedback surveys"
                ],
                "channels": ["Email", "Retargeting ads", "SMS"]
            },
            "Hibernating": {
                "actions": [
                    "Re-engagement campaigns",
                    "Major discounts",
                    "New product announcements"
                ],
                "channels": ["Email", "Social media retargeting"]
            },
            "Regular": {
                "actions": [
                    "Targeted promotions",
                    "Cross-sell opportunities",
                    "Engagement campaigns"
                ],
                "channels": ["Email", "Push notifications"]
            }
        }
        
        segment_name = self.segment_profiles[segment_id]['name']
        return recommendations.get(segment_name, recommendations["Regular"])
    
    def save(self, path: str):
        """Save the model to disk."""
        joblib.dump({
            'scaler': self.scaler,
            'kmeans': self.kmeans,
            'n_clusters': self.n_clusters,
            'cluster_centers_original': self.cluster_centers_original,
            'segment_profiles': self.segment_profiles
        }, path)
        logger.info("Model saved", path=path)
    
    @classmethod
    def load(cls, path: str) -> 'CustomerSegmentation':
        """Load a model from disk."""
        data = joblib.load(path)
        model = cls(n_clusters=data['n_clusters'])
        model.scaler = data['scaler']
        model.kmeans = data['kmeans']
        model.cluster_centers_original = data['cluster_centers_original']
        model.segment_profiles = data['segment_profiles']
        return model


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Generate sample RFM data
    n_customers = 5000
    
    rfm_data = pd.DataFrame({
        'customer_id': range(1, n_customers + 1),
        'recency': np.random.exponential(60, n_customers).astype(int),
        'frequency': np.random.poisson(5, n_customers) + 1,
        'monetary': np.random.exponential(5000, n_customers)
    })
    
    # Train model
    segmentation = CustomerSegmentation(n_clusters=6)
    segmentation.fit(rfm_data)
    
    # Print segment profiles
    print("\nSegment Profiles:")
    print("-" * 60)
    for segment_id, profile in segmentation.segment_profiles.items():
        print(f"\nSegment {segment_id}: {profile['name']}")
        print(f"  Size: {profile['size']} ({profile['percentage']:.1f}%)")
        print(f"  Avg Recency: {profile['avg_recency']:.1f} days")
        print(f"  Avg Frequency: {profile['avg_frequency']:.1f} orders")
        print(f"  Avg Monetary: ${profile['avg_monetary']:.2f}")
    
    # Segment a single customer
    customer = {'recency': 10, 'frequency': 15, 'monetary': 25000}
    result = segmentation.segment_customer(customer)
    print(f"\nCustomer segmentation: {result['segment_name']}")
