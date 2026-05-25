from .base_adapter import BaseAdapter, CircuitBreakerOpenException, SimpleCache, CircuitBreaker
from .google_books_adapter import GoogleBooksAdapter
from .open_library_adapter import OpenLibraryAdapter
from .crossref_adapter import CrossrefAdapter
from .ebay_adapter import EbayAdapter

google_books_client = GoogleBooksAdapter()
open_library_client = OpenLibraryAdapter()
crossref_client = CrossrefAdapter()
ebay_client = EbayAdapter()

def get_all_adapters_status():
    return {
        "google_books": google_books_client.get_status(),
        "open_library": open_library_client.get_status(),
        "crossref": crossref_client.get_status(),
        "ebay": ebay_client.get_status(),
    }
