import asyncio
import json
import logging
import urllib.parse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.auth import require_auth
from app.proxy import TIMEOUT, SERVICE_MAP, proxy_request

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────
# HEALTH — aggregated across all services
# ─────────────────────────────────────────

async def _ping_service(base_url: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{base_url}/health")
        if r.status_code == 200:
            return {"status": "ok", "url": base_url}
        return {"status": "degraded", "code": r.status_code, "url": base_url}
    except Exception as exc:
        return {"status": "unavailable", "error": type(exc).__name__, "url": base_url}


@router.get("/health")
async def health():
    checks = await asyncio.gather(
        *[_ping_service(url) for url in SERVICE_MAP.values()],
        return_exceptions=True,
    )
    services = dict(zip(SERVICE_MAP.keys(), checks))
    overall = "ok" if all(s.get("status") == "ok" for s in services.values()) else "degraded"
    return {
        "status": overall,
        "service": "bff-gateway",
        "version": "2.0.0",
        "services": services,
    }


# ─────────────────────────────────────────
# AUTH — convert JSON → form-urlencoded
# ─────────────────────────────────────────

@router.post("/api/auth/login")
async def auth_login(request: Request) -> Response:
    """Auth-service requires application/x-www-form-urlencoded (OAuth2PasswordRequestForm).
    Accepts both form-encoded and JSON from the frontend."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("username", "")
            password = body.get("password", "")
        except Exception:
            return JSONResponse(status_code=400, content={"detail": "Invalid JSON body"})
    else:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

    form_data = urllib.parse.urlencode({
        "username": username,
        "password": password,
        "grant_type": "password",
    }).encode()

    auth_url = SERVICE_MAP.get("auth")
    if not auth_url:
        return JSONResponse(status_code=503, content={"detail": "auth-service not configured"})

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{auth_url}/login",
                content=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        logger.error("auth-service unreachable: %s", exc)
        return JSONResponse(status_code=503, content={"detail": "auth-service unavailable"})


# ─────────────────────────────────────────
# SPRINT 2 — Admin Pricing routes
# ─────────────────────────────────────────

@router.post("/api/admin/pricing/bulk-calculate", dependencies=[Depends(require_auth)])
async def admin_pricing_bulk_calculate() -> JSONResponse:
    """Fetch all catalog products and calculate a price for each one."""
    catalog_url = SERVICE_MAP.get("catalog", "http://catalog-service:8003")
    pricing_url = SERVICE_MAP.get("pricing", "http://pricing-service:8005")

    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
        try:
            books_resp = await client.get(f"{catalog_url}/products", params={"limit": 500}, timeout=30.0)
            books_resp.raise_for_status()
            books = books_resp.json()
            if isinstance(books, dict):
                books = books.get("items", books.get("data", []))
        except Exception as exc:
            return JSONResponse(
                status_code=503,
                content={"detail": f"No se pudo obtener el catálogo: {type(exc).__name__}"},
            )

        ok_count = 0
        fail_count = 0
        for book in books:
            book_id = str(book.get("id", ""))
            book_title = book.get("title", "Sin título")
            condition = book.get("condition") or "BUENO"
            valid_conditions = {"NUEVO", "BUENO", "ACEPTABLE", "DETERIORADO"}
            if condition not in valid_conditions:
                condition = "BUENO"
            try:
                resp = await client.post(
                    f"{pricing_url}/pricing/calculate",
                    json={"book_id": book_id, "book_title": book_title, "condition": condition},
                    timeout=30.0,
                )
                if resp.status_code < 400:
                    ok_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

    return JSONResponse(content={"calculated": ok_count, "failed": fail_count, "total": len(books)})


@router.api_route(
    "/api/admin/pricing/recalculate",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def admin_pricing_recalculate(request: Request) -> Response:
    return await proxy_request("pricing", "pricing/calculate", request)


@router.api_route(
    "/api/admin/pricing/{book_id}/history",
    methods=["GET"],
)
async def admin_pricing_history(book_id: str, request: Request) -> Response:
    return await proxy_request("pricing", f"pricing/{book_id}/history", request)


@router.api_route(
    "/api/admin/pricing/{book_id}/explanation",
    methods=["GET"],
)
async def admin_pricing_explanation(book_id: str, request: Request) -> Response:
    return await proxy_request("pricing", f"pricing/{book_id}", request)


@router.api_route(
    "/api/admin/pricing/{book_id}",
    methods=["GET"],
)
async def admin_pricing_detail(book_id: str, request: Request) -> Response:
    return await proxy_request("pricing", f"pricing/{book_id}", request)


@router.api_route(
    "/api/admin/pricing",
    methods=["GET"],
)
async def admin_pricing_list(request: Request) -> Response:
    return await proxy_request("pricing", "pricing/", request)


@router.api_route(
    "/api/admin/pricing",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def admin_pricing_calculate(request: Request) -> Response:
    body_bytes = await request.body()
    response = await proxy_request("pricing", "pricing/calculate", request)
    entity_id = "unknown"
    try:
        from app.audit.repository import save_audit_entry
        body_data = json.loads(body_bytes) if body_bytes else {}
        out_data = json.loads(response.body) if response.body else {}
        entity_id = str(body_data.get("book_id", "unknown"))
        save_audit_entry(
            entity_type="pricing",
            entity_id=entity_id,
            action="calculate_price",
            service_name="pricing-service",
            input_data=body_data,
            output_data=out_data,
        )
    except Exception as exc:
        logger.warning("Audit log failed for pricing decision (book_id=%s): %s", entity_id, exc)
    return response


# ─────────────────────────────────────────
# SPRINT 2 — Admin Enrichment routes
# ─────────────────────────────────────────

@router.api_route(
    "/api/admin/enrichment/status",
    methods=["GET"],
)
async def admin_enrichment_status(request: Request) -> Response:
    return await proxy_request("enrichment", "external-apis/status", request)


@router.api_route(
    "/api/admin/enrichment/trigger",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def admin_enrichment_trigger(request: Request) -> Response:
    body_bytes = await request.body()
    response = await proxy_request("enrichment", "enrich", request)
    entity_id = "unknown"
    try:
        from app.audit.repository import save_audit_entry
        body_data = json.loads(body_bytes) if body_bytes else {}
        out_data = json.loads(response.body) if response.body else {}
        entity_id = str(body_data.get("book_id", out_data.get("request_id", "unknown")))
        save_audit_entry(
            entity_type="enrichment",
            entity_id=entity_id,
            action="trigger_enrichment",
            service_name="ai-enrichment-service",
            input_data=body_data,
            output_data=out_data,
        )
    except Exception as exc:
        logger.warning("Audit log failed for enrichment trigger (id=%s): %s", entity_id, exc)
    return response


@router.api_route(
    "/api/admin/enrichment/upload-excel",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def admin_enrichment_upload_excel(request: Request) -> Response:
    return await proxy_request("enrichment", "upload-excel", request)


@router.api_route(
    "/api/admin/enrichment/{path:path}",
    methods=["GET", "POST"],
    dependencies=[Depends(require_auth)],
)
async def admin_enrichment_path(path: str, request: Request) -> Response:
    return await proxy_request("enrichment", f"enrich/{path}", request)


# ─────────────────────────────────────────
# SPRINT 3 — Orders routes
# ─────────────────────────────────────────

@router.api_route(
    "/api/orders/{order_id}/confirm",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def order_confirm(order_id: int, request: Request) -> Response:
    return await proxy_request("order", f"orders/{order_id}/confirm", request)


@router.api_route(
    "/api/orders/{order_id}/cancel",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def order_cancel(order_id: int, request: Request) -> Response:
    return await proxy_request("order", f"orders/{order_id}/cancel", request)


@router.api_route(
    "/api/orders/{order_id}/fulfill",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def order_fulfill(order_id: int, request: Request) -> Response:
    return await proxy_request("order", f"orders/{order_id}/fulfill", request)


@router.api_route(
    "/api/orders/{order_id}",
    methods=["GET"],
)
async def order_detail(order_id: int, request: Request) -> Response:
    return await proxy_request("order", f"orders/{order_id}", request)


@router.api_route(
    "/api/orders",
    methods=["GET", "POST"],
)
async def orders_root(request: Request) -> Response:
    body_bytes = await request.body()
    response = await proxy_request("order", "orders", request)
    if request.method == "POST":
        entity_id = "unknown"
        try:
            from app.audit.repository import save_audit_entry
            body_data = json.loads(body_bytes) if body_bytes else {}
            out_data = json.loads(response.body) if response.body else {}
            entity_id = str(out_data.get("id", body_data.get("book_id", "unknown")))
            save_audit_entry(
                entity_type="order",
                entity_id=entity_id,
                action="create_order",
                service_name="order-service",
                input_data=body_data,
                output_data=out_data,
            )
        except Exception as exc:
            logger.warning("Audit log failed for order creation (id=%s): %s", entity_id, exc)
    return response


# ─────────────────────────────────────────
# SPRINT 3 — Cart routes (via order-service)
# ─────────────────────────────────────────

@router.api_route(
    "/api/cart",
    methods=["GET", "DELETE"],
    dependencies=[Depends(require_auth)],
)
async def cart_root(request: Request, payload: dict = Depends(require_auth)) -> Response:
    customer_id = str(payload.get("sub", payload.get("user_id", "anonymous")))
    return await proxy_request("order", f"cart/{customer_id}", request)


@router.api_route(
    "/api/cart/items",
    methods=["POST"],
    dependencies=[Depends(require_auth)],
)
async def cart_add_item(request: Request, payload: dict = Depends(require_auth)) -> Response:
    customer_id = str(payload.get("sub", payload.get("user_id", "anonymous")))
    return await proxy_request("order", f"cart/{customer_id}/items", request)


@router.api_route(
    "/api/cart/items/{book_id}",
    methods=["DELETE"],
    dependencies=[Depends(require_auth)],
)
async def cart_remove_item(book_id: str, request: Request, payload: dict = Depends(require_auth)) -> Response:
    customer_id = str(payload.get("sub", payload.get("user_id", "anonymous")))
    return await proxy_request("order", f"cart/{customer_id}/items/{book_id}", request)


# ─────────────────────────────────────────
# SPRINT 3 — Chat (AI Assistant)
# ─────────────────────────────────────────

@router.api_route("/api/chat", methods=["POST"])
@router.api_route("/api/assistant/ask", methods=["POST"])
async def chat(request: Request) -> Response:
    assistant_url = SERVICE_MAP.get("assistant", "http://ai-assistant-service:8011")
    url = f"{assistant_url}/chat"
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length")}
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
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
        raise HTTPException(status_code=503, detail=f"Asistente no disponible: {type(exc).__name__}")


# ─────────────────────────────────────────
# SPRINT 3 — Recommendations
# ─────────────────────────────────────────

@router.api_route(
    "/api/recommendations/{book_id}",
    methods=["GET"],
)
async def recommendations(book_id: str, request: Request) -> Response:
    return await proxy_request("recommendations", f"recommendations/{book_id}", request)


# ─────────────────────────────────────────
# SPRINT 3 — Audit
# ─────────────────────────────────────────

@router.api_route("/api/admin/audit/stats", methods=["GET"])
async def audit_stats(request: Request) -> Response:
    from app.audit.repository import get_audit_stats
    stats = get_audit_stats()
    return JSONResponse(content=stats)


@router.api_route("/api/admin/audit/pricing", methods=["GET"])
async def audit_pricing(request: Request) -> Response:
    from app.audit.repository import list_audit_entries
    entries = list_audit_entries(entity_type="pricing")
    return JSONResponse(content=entries)


@router.api_route("/api/admin/audit/orders", methods=["GET"])
async def audit_orders(request: Request) -> Response:
    from app.audit.repository import list_audit_entries
    entries = list_audit_entries(entity_type="order")
    return JSONResponse(content=entries)


@router.api_route("/api/admin/audit/enrichment", methods=["GET"])
async def audit_enrichment(request: Request) -> Response:
    from app.audit.repository import list_audit_entries
    entries = list_audit_entries(entity_type="enrichment")
    return JSONResponse(content=entries)


@router.api_route("/api/admin/audit/anomalies", methods=["GET"])
async def audit_anomalies(request: Request) -> Response:
    from app.audit.repository import get_audit_anomalies
    anomalies = get_audit_anomalies()
    return JSONResponse(content=anomalies)


@router.api_route("/api/admin/audit/{entry_id}", methods=["GET"])
async def audit_entry_detail(entry_id: str, request: Request) -> Response:
    from app.audit.repository import get_audit_entry
    entry = get_audit_entry(entry_id)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return JSONResponse(content=entry)


# ─────────────────────────────────────────
# Enriched catalog — merges pricing data
# ─────────────────────────────────────────

async def _fetch_price(client: httpx.AsyncClient, pricing_url: str, book_id: str) -> dict | None:
    try:
        r = await client.get(f"{pricing_url}/pricing/{book_id}", timeout=3.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


async def _fetch_availability(
    client: httpx.AsyncClient, inventory_url: str, book_reference: str
) -> dict | None:
    if not book_reference:
        return None
    try:
        r = await client.get(
            f"{inventory_url}/inventory/availability/{book_reference}", timeout=3.0
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@router.get("/api/catalog/books/{book_id}")
@router.get("/api/catalog/products/{book_id}")
async def catalog_book_enriched(book_id: str, request: Request) -> JSONResponse:
    catalog_url = SERVICE_MAP.get("catalog", "http://catalog-service:8003")
    pricing_url = SERVICE_MAP.get("pricing", "http://pricing-service:8005")
    inventory_url = SERVICE_MAP.get("inventory", "http://inventory-service:8002")

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            book_resp = await client.get(
                f"{catalog_url}/products/{book_id}",
                headers={k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")},
            )
            if book_resp.status_code != 200:
                return Response(content=book_resp.content, status_code=book_resp.status_code,
                                media_type="application/json")
            book = book_resp.json()
        except Exception as exc:
            return JSONResponse(status_code=503, content={"detail": f"catalog unavailable: {type(exc).__name__}"})

        book_ref = book.get("isbn") or ""
        pricing, availability = await asyncio.gather(
            _fetch_price(client, pricing_url, book_id),
            _fetch_availability(client, inventory_url, book_ref),
            return_exceptions=True,
        )

        if isinstance(pricing, dict) and pricing:
            book["suggested_price"] = pricing.get("suggested_price")
            book["is_fallback"] = pricing.get("is_fallback", False)
            book["price_source"] = pricing.get("source")

        if isinstance(availability, dict) and availability:
            book["quantity_available"] = availability.get("quantity_available", 0)
            book["is_available"] = availability.get("is_available", False)
        else:
            book["quantity_available"] = None
            book["is_available"] = None

    return JSONResponse(content=book)


@router.get("/api/catalog/books")
@router.get("/api/catalog/products")
async def catalog_books_enriched(request: Request) -> JSONResponse:
    catalog_url = SERVICE_MAP.get("catalog", "http://catalog-service:8003")
    pricing_url = SERVICE_MAP.get("pricing", "http://pricing-service:8005")
    inventory_url = SERVICE_MAP.get("inventory", "http://inventory-service:8002")

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            books_resp = await client.get(
                f"{catalog_url}/products",
                params=dict(request.query_params),
                headers={k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")},
            )
            if books_resp.status_code != 200:
                return Response(content=books_resp.content, status_code=books_resp.status_code,
                                media_type="application/json")
            payload = books_resp.json()
        except Exception as exc:
            return JSONResponse(status_code=503, content={"detail": f"catalog unavailable: {type(exc).__name__}"})

        books: list[dict] = payload if isinstance(payload, list) else payload.get("items", payload.get("data", []))

        price_tasks = [_fetch_price(client, pricing_url, str(b.get("id", ""))) for b in books]
        avail_tasks = [_fetch_availability(client, inventory_url, b.get("isbn") or "") for b in books]

        results = await asyncio.gather(*price_tasks, *avail_tasks, return_exceptions=True)
        prices = results[: len(books)]
        availabilities = results[len(books) :]

        enriched = []
        for book, price_result, avail_result in zip(books, prices, availabilities):
            merged = dict(book)
            if isinstance(price_result, dict) and price_result:
                merged["suggested_price"] = price_result.get("suggested_price")
                merged["is_fallback"] = price_result.get("is_fallback", False)
                merged["price_source"] = price_result.get("source")
            if isinstance(avail_result, dict) and avail_result:
                merged["quantity_available"] = avail_result.get("quantity_available", 0)
                merged["is_available"] = avail_result.get("is_available", False)
            else:
                merged["quantity_available"] = None
                merged["is_available"] = None
            enriched.append(merged)

        if isinstance(payload, list):
            return JSONResponse(content=enriched)
        return JSONResponse(content={**payload, "items": enriched} if "items" in payload
                            else {**payload, "data": enriched})


# ─────────────────────────────────────────
# GENERIC catch-all proxy
# ─────────────────────────────────────────

@router.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request) -> Response:
    return await proxy_request(service, path, request)


@router.api_route("/api/{service}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_root(service: str, request: Request) -> Response:
    return await proxy_request(service, "", request)
