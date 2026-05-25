# Recommendation Service

Microservicio de recomendaciones para la plataforma. Sugiere productos relacionados basándose en marca y categoría, filtrando artículos agotados.

## ¿Qué hace?

- Recomienda libros por mismo autor (score 1.0)
- Recomienda libros por misma categoría (score 0.8)
- Filtra libros agotados consultando el Inventory Service
- Ordena resultados por relevancia

## Endpoint principal

GET /recommendations/{book_id}

Retorna una lista de libros recomendados para el libro con el ID dado.

### Ejemplo de respuesta

```json
[
  {
    "book_id": "2",
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "category": "1",
    "score": 1.0,
    "reason": "Same author: Robert C. Martin"
  }
]
```

## Health Check

GET /health

## Variables de entorno

| Variable | Valor por defecto | Descripción |
|---|---|---|
| CATALOG_SERVICE_URL | http://catalog-service:8003 | URL del catálogo |
| INVENTORY_SERVICE_URL | http://inventory-service:8001 | URL del inventario |
| HTTP_TIMEOUT | 5.0 | Timeout en segundos |
| SERVICE_PORT | 8012 | Puerto del servicio |
| MAX_RECOMMENDATIONS | 10 | Máximo de sugerencias |

## Ejecutar localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8012
```

## Ejecutar tests

```bash
pytest tests/ -v
```

## Servicios relacionados

- **catalog-service** — provee la lista de libros
- **inventory-service** — valida disponibilidad de stock