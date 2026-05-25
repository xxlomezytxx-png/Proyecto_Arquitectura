# Inventory Service — BookFlow

Carga masiva y gestión de inventario. Puerto **8002**.

## Endpoints
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/batches/upload` | Carga CSV/XLSX |
| GET | `/batches/` | Listar lotes |
| GET | `/batches/{id}` | Detalle lote |
| GET | `/batches/{id}/errors` | Errores del lote |
| GET | `/batches/{id}/items` | Ítems del lote |
| GET | `/inventory/` | Listar ítems |
| GET | `/inventory/{id}` | Detalle ítem |
| GET | `/inventory/availability/{ref}` | Disponibilidad |
| GET | `/health` | Health check |

## Formato CSV requerido
```
title, author, book_reference, quantity_available
```
Opcionales: `isbn`, `condition` (new/like_new/good/acceptable/poor), `defects`, `observations`, `external_code`

## Ejecución local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```
