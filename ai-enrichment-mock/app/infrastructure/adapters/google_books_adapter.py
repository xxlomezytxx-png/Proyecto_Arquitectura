from .base_adapter import BaseAdapter

class GoogleBooksAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="GoogleBooks",
            base_url="https://www.googleapis.com/books/v1",
            failure_threshold=3,
            cooldown_seconds=30,
            cache_ttl=3600,
            timeout=5
        )

    def search_by_isbn(self, isbn: str):
        return self.fetch(
            endpoint="/volumes",
            cache_kwargs={"isbn": isbn},
            params={"q": f"isbn:{isbn}"}
        )

    def search_by_query(self, query: str):
        return self.fetch(
            endpoint="/volumes",
            cache_kwargs={"query": query},
            params={"q": query}
        )
