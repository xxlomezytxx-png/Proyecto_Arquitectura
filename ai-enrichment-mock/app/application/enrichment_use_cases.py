from typing import List
from app.domain.enrichment import EnrichmentRequest, EnrichmentResult, build_mock_result


def enrich_single(req: EnrichmentRequest) -> EnrichmentResult:
    return build_mock_result(req)


def enrich_batch(requests: List[EnrichmentRequest]) -> List[EnrichmentResult]:
    return [build_mock_result(r) for r in requests]
