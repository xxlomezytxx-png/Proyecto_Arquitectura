import os
import httpx
from fastapi import Request, Response, HTTPException

TIMEOUT = 600.0

SERVICE_MAP = {
    "auth":            os.getenv("AUTH_SERVICE_URL",       "http://auth-service:8001"),
    "inventory":       os.getenv("INVENTORY_SERVICE_URL",  "http://inventory-service:8002"),
    "catalog":         os.getenv("CATALOG_SERVICE_URL",    "http://catalog-service:8003"),
    "enrichment":      os.getenv("ENRICHMENT_SERVICE_URL", "http://ai-enrichment-service:8004"),
    "pricing":         os.getenv("PRICING_SERVICE_URL",    "http://pricing-service:8005"),
    "quality":         os.getenv("DATA_QUALITY_URL",       "http://data-quality-module:8007"),
    "config":          os.getenv("CONFIG_MODULE_URL",      "http://config-module:8008"),
    "order":           os.getenv("ORDER_SERVICE_URL",          "http://order-service:8010"),
    "assistant":       os.getenv("ASSISTANT_SERVICE_URL",      "http://ai-assistant-service:8011"),
    "recommendations": os.getenv("RECOMMENDATION_SERVICE_URL", "http://recommendation-service:8012"),
}


async def proxy_request(service_name: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service_name)
    if base_url is None:
        if service_name == "assistant":
            base_url = os.getenv("ASSISTANT_SERVICE_URL", "http://ai-assistant-service:8011")
            SERVICE_MAP["assistant"] = base_url
        else:
            raise HTTPException(status_code=404, detail=f"Servicio '{service_name}' no registrado")

    url = f"{base_url}/{path}" if path else base_url
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length")}

    try:
        body = await request.body()
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            upstream = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=dict(upstream.headers),
            media_type=upstream.headers.get("content-type", "application/json"),
        )
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Servicio '{service_name}' no disponible: {type(exc).__name__}",
        )
