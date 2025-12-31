"""Customer segmentation endpoints."""

from typing import List
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class RFMData(BaseModel):
    customer_id: int
    recency: int  # days since last purchase
    frequency: int  # number of purchases
    monetary: float  # total spend


class SegmentationRequest(BaseModel):
    customers: List[RFMData]


class CustomerSegment(BaseModel):
    customer_id: int
    segment_id: int
    segment_name: str
    rfm_score: str


@router.post("/segment", response_model=List[CustomerSegment])
async def segment_customers(
    request: SegmentationRequest,
    req: Request
):
    """Segment customers based on RFM metrics."""
    model_manager = req.app.state.model_manager
    
    results = []
    for customer in request.customers:
        segment = model_manager.segment_customer({
            "recency": customer.recency,
            "frequency": customer.frequency,
            "monetary": customer.monetary
        })
        
        # Calculate RFM score
        r_score = 5 if customer.recency < 30 else 4 if customer.recency < 60 else 3 if customer.recency < 90 else 2 if customer.recency < 180 else 1
        f_score = min(5, max(1, customer.frequency // 2))
        m_score = 5 if customer.monetary > 50000 else 4 if customer.monetary > 20000 else 3 if customer.monetary > 10000 else 2 if customer.monetary > 5000 else 1
        
        results.append(CustomerSegment(
            customer_id=customer.customer_id,
            segment_id=segment["segment_id"],
            segment_name=segment["segment_name"],
            rfm_score=f"{r_score}{f_score}{m_score}"
        ))
    
    return results


@router.get("/segments")
async def get_segment_definitions():
    """Get all segment definitions and their criteria."""
    return {
        "segments": [
            {
                "id": 0,
                "name": "Champions",
                "description": "Best customers with high recency, frequency, and monetary value",
                "criteria": "R < 30, F >= 10, M >= 10000",
                "recommended_action": "Reward with exclusive offers, early access to new products"
            },
            {
                "id": 1,
                "name": "Loyal",
                "description": "Regular customers with consistent purchases",
                "criteria": "R < 60, F >= 5",
                "recommended_action": "Upsell higher value products, loyalty program"
            },
            {
                "id": 2,
                "name": "New Customers",
                "description": "Recently acquired customers with few purchases",
                "criteria": "R < 30, F < 3",
                "recommended_action": "Onboarding emails, first purchase discounts"
            },
            {
                "id": 3,
                "name": "At Risk",
                "description": "Previously active customers showing signs of churn",
                "criteria": "R >= 90, F >= 5",
                "recommended_action": "Win-back campaigns, personalized offers"
            },
            {
                "id": 4,
                "name": "Hibernating",
                "description": "Inactive customers who haven't purchased recently",
                "criteria": "R >= 90",
                "recommended_action": "Re-engagement campaigns, surveys"
            },
            {
                "id": 5,
                "name": "Regular",
                "description": "Average customers with moderate activity",
                "criteria": "Default segment",
                "recommended_action": "Maintain engagement, targeted promotions"
            }
        ]
    }
