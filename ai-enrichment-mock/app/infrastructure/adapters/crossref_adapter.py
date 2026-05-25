from .base_adapter import BaseAdapter

class CrossrefAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="Crossref",
            base_url="https://api.crossref.org",
            failure_threshold=3,
            cooldown_seconds=60,
            cache_ttl=86400, # 1 day
            timeout=10
        )

    def search_by_query(self, query: str):
        return self.fetch(
            endpoint="/works",
            cache_kwargs={"query": query},
            params={"query": query}
        )
