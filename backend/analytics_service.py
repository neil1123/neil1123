import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from ga4mp import GtagMP
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Comprehensive analytics service for Doord marketplace
    Handles both Google Analytics 4 and custom business metrics
    """
    
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.measurement_id = os.getenv("GA_MEASUREMENT_ID")
        self.api_secret = os.getenv("GA_API_SECRET")
        self.db = db
        
        # Initialize GA4 client
        if self.measurement_id and self.api_secret:
            self.ga4 = GtagMP(
                measurement_id=self.measurement_id,
                api_secret=self.api_secret
            )
        else:
            logger.warning("GA4 credentials not found in environment variables")
            self.ga4 = None
    
    async def track_event(
        self, 
        client_id: str, 
        event_name: str, 
        event_params: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None
    ):
        """Track event to both GA4 and MongoDB"""
        if event_params is None:
            event_params = {}
            
        # Add timestamp and common properties
        event_params.update({
            'timestamp': datetime.utcnow().isoformat(),
            'platform': 'doord_marketplace'
        })
        
        # Track to GA4
        if self.ga4:
            try:
                event_data = {
                    "client_id": client_id,
                    "events": [{
                        "name": event_name,
                        "params": event_params
                    }]
                }
                
                if user_properties:
                    event_data["user_properties"] = user_properties
                
                # Send to GA4 (non-blocking)
                asyncio.create_task(self._send_to_ga4(event_data))
                
            except Exception as e:
                logger.error(f"Failed to send event to GA4: {e}")
        
        # Store in MongoDB for backup and custom analytics
        if self.db:
            try:
                await self.db.analytics_events.insert_one({
                    "client_id": client_id,
                    "event_name": event_name,
                    "event_params": event_params,
                    "user_properties": user_properties,
                    "created_at": datetime.utcnow()
                })
            except Exception as e:
                logger.error(f"Failed to store event in MongoDB: {e}")
    
    async def _send_to_ga4(self, event_data: Dict[str, Any]):
        """Send event to GA4 (async wrapper)"""
        try:
            # GA4MP library is synchronous, so run in thread pool
            import concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, self.ga4.send, event_data)
        except Exception as e:
            logger.error(f"GA4 send error: {e}")

    # === USER JOURNEY TRACKING ===
    
    async def track_page_view(self, client_id: str, page_path: str, user_type: str = None):
        """Track page view with user context"""
        await self.track_event(
            client_id=client_id,
            event_name="page_view",
            event_params={
                "page_path": page_path,
                "page_title": self._get_page_title(page_path)
            },
            user_properties={"user_type": user_type} if user_type else None
        )
    
    async def track_signup(self, client_id: str, user_type: str, signup_method: str = "email"):
        """Track user registration"""
        await self.track_event(
            client_id=client_id,
            event_name="sign_up",
            event_params={
                "method": signup_method,
                "user_type": user_type
            },
            user_properties={"user_type": user_type}
        )
    
    async def track_login(self, client_id: str, user_type: str):
        """Track user login"""
        await self.track_event(
            client_id=client_id,
            event_name="login",
            event_params={"method": "email"},
            user_properties={"user_type": user_type}
        )
    
    # === BUSINESS METRICS ===
    
    async def track_quotation_request(self, client_id: str, provider_id: str, service_type: str, estimated_value: float = None):
        """Track quotation requests (top of funnel)"""
        params = {
            "provider_id": provider_id,
            "service_type": service_type,
            "funnel_step": "quotation_request"
        }
        if estimated_value:
            params["estimated_value"] = estimated_value
            params["currency"] = "USD"
            
        await self.track_event(
            client_id=client_id,
            event_name="quotation_request",
            event_params=params
        )
    
    async def track_quotation_sent(self, client_id: str, quotation_id: str, amount: float, provider_id: str):
        """Track when provider sends quotation"""
        await self.track_event(
            client_id=client_id,
            event_name="quotation_sent",
            event_params={
                "quotation_id": quotation_id,
                "value": amount,
                "currency": "USD",
                "provider_id": provider_id,
                "funnel_step": "quotation_sent"
            }
        )
    
    async def track_booking(self, client_id: str, booking_id: str, provider_id: str, amount: float, service_type: str, is_first_booking: bool = False):
        """Track successful booking (conversion)"""
        event_name = "first_booking" if is_first_booking else "repeat_booking"
        
        await self.track_event(
            client_id=client_id,
            event_name=event_name,
            event_params={
                "booking_id": booking_id,
                "provider_id": provider_id,
                "value": amount,
                "currency": "USD",
                "service_type": service_type,
                "funnel_step": "booking_confirmed"
            }
        )
    
    async def track_booking_completion(self, client_id: str, booking_id: str, provider_id: str, final_amount: float, provider_earnings: float):
        """Track booking completion (revenue)"""
        await self.track_event(
            client_id=client_id,
            event_name="booking_completed",
            event_params={
                "booking_id": booking_id,
                "provider_id": provider_id,
                "value": final_amount,  # GMV
                "currency": "USD",
                "provider_earnings": provider_earnings,
                "platform_fee": final_amount - provider_earnings,
                "funnel_step": "booking_completed"
            }
        )
    
    async def track_review_submitted(self, client_id: str, provider_id: str, rating: int, booking_id: str = None):
        """Track review submission"""
        await self.track_event(
            client_id=client_id,
            event_name="review_submitted",
            event_params={
                "provider_id": provider_id,
                "rating": rating,
                "booking_id": booking_id
            }
        )
    
    # === MARKETPLACE KPIS ===
    
    async def track_provider_earnings(self, provider_id: str, amount: float, booking_id: str):
        """Track provider earnings for provider analytics"""
        await self.track_event(
            client_id=provider_id,
            event_name="provider_earning",
            event_params={
                "value": amount,
                "currency": "USD",
                "booking_id": booking_id
            },
            user_properties={"user_type": "provider"}
        )
    
    async def track_search(self, client_id: str, search_query: str, results_count: int, location: str = None):
        """Track service searches"""
        params = {
            "search_query": search_query,
            "results_count": results_count
        }
        if location:
            params["location"] = location
            
        await self.track_event(
            client_id=client_id,
            event_name="search",
            event_params=params
        )
    
    # === ENGAGEMENT METRICS ===
    
    async def track_dashboard_view(self, client_id: str, user_type: str, metrics_viewed: Dict[str, Any] = None):
        """Track dashboard usage"""
        params = {"dashboard_type": f"{user_type}_dashboard"}
        if metrics_viewed:
            params.update(metrics_viewed)
            
        await self.track_event(
            client_id=client_id,
            event_name="dashboard_view",
            event_params=params,
            user_properties={"user_type": user_type}
        )
    
    async def track_message_sent(self, sender_id: str, recipient_id: str, message_type: str = "text"):
        """Track messaging activity"""
        await self.track_event(
            client_id=sender_id,
            event_name="message_sent",
            event_params={
                "recipient_id": recipient_id,
                "message_type": message_type
            }
        )
    
    # === CUSTOM ANALYTICS ===
    
    async def get_conversion_funnel(self, start_date: datetime, end_date: datetime):
        """Get conversion funnel metrics from MongoDB"""
        if not self.db:
            return None
            
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date},
                    "event_name": {"$in": ["quotation_request", "quotation_sent", "first_booking", "booking_completed"]}
                }
            },
            {
                "$group": {
                    "_id": "$event_name",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        result = await self.db.analytics_events.aggregate(pipeline).to_list(10)
        return {item["_id"]: item["count"] for item in result}
    
    async def get_gmv_metrics(self, start_date: datetime, end_date: datetime):
        """Get GMV and revenue metrics"""
        if not self.db:
            return None
            
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date},
                    "event_name": "booking_completed"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_gmv": {"$sum": "$event_params.value"},
                    "total_provider_earnings": {"$sum": "$event_params.provider_earnings"},
                    "total_platform_fees": {"$sum": "$event_params.platform_fee"},
                    "booking_count": {"$sum": 1}
                }
            }
        ]
        
        result = await self.db.analytics_events.aggregate(pipeline).to_list(1)
        return result[0] if result else {}
    
    def _get_page_title(self, page_path: str) -> str:
        """Convert page path to readable title"""
        titles = {
            "/": "Homepage",
            "/homeowners": "Homeowner Landing",
            "/homeowners/browse": "Browse Services", 
            "/homeowners/auth": "Homeowner Auth",
            "/homeowners/dashboard": "Homeowner Dashboard",
            "/homeservices": "Provider Landing",
            "/homeservices/auth": "Provider Auth",
            "/homeservices/dashboard": "Provider Dashboard",
            "/homeservices/analytics": "Provider Analytics",
            "/homeservices/orders": "Provider Orders",
            "/homeservices/profile": "Provider Profile"
        }
        return titles.get(page_path, page_path)

# Global analytics instance (will be initialized in main.py)
analytics_service = None