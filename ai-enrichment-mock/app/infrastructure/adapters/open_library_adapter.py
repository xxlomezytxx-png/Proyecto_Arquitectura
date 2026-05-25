from .base_adapter import BaseAdapter

class OpenLibraryAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="OpenLibrary",
            base_url="https://openlibrary.org",
            failure_threshold=3,
            cooldown_seconds=45,
            cache_ttl=7200,
            timeout=5
        )

    def search_by_isbn(self, isbn: str):
        return self.fetch(
            endpoint=f"/isbn/{isbn}.json",
            cache_kwargs={"isbn": isbn}
        )

    def search_by_query(self, query: str):
        return self.fetch(
            endpoint="/search.json",
            cache_kwargs={"query": query},
            params={"q": query}
        )
