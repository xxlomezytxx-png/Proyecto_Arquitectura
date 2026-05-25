class UpstreamServiceError(RuntimeError):
    """Raised when an upstream service is unreachable or returns 5xx."""

    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"{service}: {message}")
        self.service = service
