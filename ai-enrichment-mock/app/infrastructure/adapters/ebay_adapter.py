from .base_adapter import BaseAdapter

class EbayAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="eBay",
            base_url="https://svcs.ebay.com/services/search/FindingService/v1",
            failure_threshold=5,
            cooldown_seconds=60,
            cache_ttl=1800, # 30 min cache for pricing logic
            timeout=5
        )

    def search_by_keyword(self, keyword: str):
        return self.fetch(
            endpoint="",
            cache_kwargs={"keyword": keyword},
            params={
                "OPERATION-NAME": "findItemsByKeywords",
                "SERVICE-VERSION": "1.0.0",
                "SECURITY-APPNAME": "mock_app_id", # Mock app id
                "RESPONSE-DATA-FORMAT": "JSON",
                "REST-PAYLOAD": "true",
                "keywords": keyword
            }
        )
