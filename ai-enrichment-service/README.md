# AI Enrichment Service — Tienda de Hardware IA

Servicio de enriquecimiento bibliográfico que consulta APIs externas (Google Books, Open Library, Crossref) para normalizar y completar los metadatos de libros en el catálogo.

**Puerto:** 8004  
**Sprint:** 2  
**Base de datos:** `enrichment_db` (PostgreSQL)

---

## Descripción

El AI Enrichment Service recibe referencias de libros (por ISBN o título/autor) y las enriquece consultando APIs externas en orden de prioridad. Los datos provenientes de fuentes heterogéneas se normalizan antes de persistirse y devolverse. Si todas las fuentes fallan, retorna datos parciales con indicador de error.

---

## Arquitectura

```
ai-enrichment-service/
├── app/
│   ├── routers/
│   │   └── enrichment_router.py         # HTTP routes, sin lógica de negocio
│   ├── application/
│   │   ├── use_cases/
│   │   │   └── enrich_book.py           # Orquestación del enriquecimiento
│   │   └── normalizer/
│   │       ├── text_normalizer.py       # Normalización de texto
│   │       ├── isbn_validator.py        # Validación y conversión ISBN
│   │       ├── author_formatter.py      # Formato estándar de autores
│   │       ├── source_merger.py         # Fusión de resultados multi-fuente
│   │       └── duplicate_detector.py   # Detección de duplicados
│   ├── domain/
│   │   └── entities/
│   │       └── enrichment.py            # Entidades puras (sin FastAPI/SQLAlchemy)
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── models.py
│   │   │   └── repositories/
│   │   └── adapters/
│   │       ├── base_adapter.py          # CircuitBreaker y SimpleCache compartidos
│   │       ├── google_books_adapter.py  # Google Books API
│   │       ├── open_library_adapter.py  # Open Library API
│   │       └── crossref_adapter.py      # Crossref API
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Endpoints

### `POST /enrich`

Solicita el enriquecimiento de un libro.

**Request:**
```json
{
  "book_id": "550e8400-e29b-41d4-a716-446655440000",
  "isbn": "9780141439518",
  "title": "Great Expectations",
  "author": "Charles Dickens",
  "publisher": "Penguin Classics"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `book_id` | string (UUID) | Sí | Identificador en el catálogo |
| `isbn` | string | No* | ISBN-13 del libro |
| `title` | string | No* | Título del libro |
| `author` | string | No | Autor |
| `publisher` | string | No | Editorial |

> *Se requiere al menos `isbn` **o** `title`.

**Response 200 — completado:**
```json
{
  "request_id": "7b4e2a1c-...",
  "status": "completed",
  "normalized_title": "Great Expectations",
  "normalized_author": "Dickens, Charles",
  "normalized_publisher": "Penguin Classics",
  "normalized_description": "The story of Pip, a young orphan...",
  "cover_url": "https://books.google.com/books/content?id=...",
  "source_used": "google_books",
  "confidence_score": 0.95
}
```

**Response 200 — fallback sin fuentes:**
```json
{
  "request_id": "7b4e2a1c-...",
  "status": "failed",
  "normalized_title": "Great Expectations",
  "normalized_author": null,
  "normalized_publisher": null,
  "normalized_description": null,
  "cover_url": null,
  "source_used": "none",
  "confidence_score": 0.0
}
```

---

### `GET /enrich/{request_id}`

Consulta el estado y resultado de una solicitud de enriquecimiento.

**Response 200:**
```json
{
  "request_id": "7b4e2a1c-...",
  "book_id": "550e8400-...",
  "status": "completed",
  "source_used": "google_books",
  "requested_at": "2026-04-12T10:00:00Z",
  "result": {
    "normalized_title": "Great Expectations",
    "normalized_author": "Dickens, Charles",
    "normalized_publisher": "Penguin Classics",
    "normalized_description": "...",
    "cover_url": "https://...",
    "confidence_score": 0.95,
    "created_at": "2026-04-12T10:00:02Z"
  }
}
```

**Response 404:** `{"detail": "Enrichment request {request_id} not found"}`

---

### `GET /external-apis/status`

Estado de los circuit breakers de las tres APIs externas.

**Response 200:**
```json
{
  "google_books": {
    "status": "healthy",
    "failure_count": 0,
    "is_open": false,
    "last_failure": null
  },
  "open_library": {
    "status": "degraded",
    "failure_count": 5,
    "is_open": true,
    "last_failure": "2026-04-12T09:55:00Z"
  },
  "crossref": {
    "status": "healthy",
    "failure_count": 1,
    "is_open": false,
    "last_failure": "2026-04-12T09:50:00Z"
  }
}
```

---

### `GET /health`

**Response 200:**
```json
{
  "status": "ok",
  "service": "ai-enrichment-service",
  "version": "2.0.0"
}
```

---

## Lógica de Enriquecimiento

### Prioridad de fuentes

```
Solicitud recibida (ISBN o título/autor)
         │
         ▼
   Google Books ──── ISBN disponible → search_by_isbn()
         │           Sin ISBN         → search_by_title_author()
         │
   ¿Encontrado? ──── Sí → guardar candidato
         │
         ▼
   Open Library ──── get_by_isbn() o search()
         │
   ¿Encontrado? ──── Sí → guardar candidato
         │
         ▼
     Crossref ──────  search_works()
         │
   ¿Encontrado? ──── Sí → guardar candidato
         │
         ▼
   ¿Hay candidatos? ── No → status="failed", retornar datos parciales
         │
         Sí
         ▼
   merge_results(candidatos) → resultado normalizado
         │
         ▼
   Persistir EnrichmentResult, status="completed"
```

### Módulo Normalizer

| Módulo | Función |
|--------|---------|
| `text_normalizer.py` | Strip, title_case, remover caracteres de control |
| `isbn_validator.py` | Validar checksum, convertir ISBN-10 → ISBN-13 |
| `author_formatter.py` | `"Nombre Apellido"` → `"Apellido, Nombre"`, múltiples autores con `;` |
| `source_merger.py` | Fusión multi-fuente; en conflicto, preferir mayor `confidence_score` |
| `duplicate_detector.py` | Detección por ISBN/ISSN antes de persistir |

**Reglas de normalización:**
- Título: strip + title_case + remover caracteres de control
- Autor: `"Charles Dickens"` → `"Dickens, Charles"`; varios autores: `"Apellido1, Nombre1; Apellido2, Nombre2"`
- ISBN: validar checksum; ISBN-10 convertido automáticamente a ISBN-13

### Circuit Breaker — por API

Cada adaptador tiene su propio circuit breaker independiente:

- Se abre tras **5 fallos consecutivos**
- Permanece abierto **5 minutos** (300 segundos)
- Durante ese tiempo: la fuente se salta automáticamente y se intenta la siguiente
- Cooldown vence → circuit breaker se cierra y la fuente vuelve a intentarse

### Caché en memoria

- TTL: **3600 segundos** (1 hora)
- Dict en memoria, se vacía al reiniciar el servicio (comportamiento aceptado)
- Evita llamadas repetidas a APIs externas para el mismo ISBN/query

---

## Variables de entorno

```env
# Base de datos
DATABASE_URL=postgresql://bookflow:bookflow@enrichment-db:5432/enrichment_db

# Google Books API
GOOGLE_BOOKS_API_KEY=TU_GOOGLE_BOOKS_KEY_AQUI

# Open Library (sin API key)
OPEN_LIBRARY_BASE_URL=https://openlibrary.org

# Crossref (sin API key)
CROSSREF_BASE_URL=https://api.crossref.org

# Servicio destino para actualizar catálogo
CATALOG_SERVICE_URL=http://catalog-service:8001

# Puerto
SERVICE_PORT=8004
```

Copiar desde `.env.example` y completar con credenciales del equipo.

> **Nota:** Open Library y Crossref no requieren API key. Solo Google Books necesita credencial.

---

## Cómo ejecutar

### Con Docker Compose (recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up ai-enrichment-service enrichment-db

# Verificar que levantó
curl http://localhost:8004/health
```

### Localmente (desarrollo)

```bash
cd ai-enrichment-service

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env (agregar GOOGLE_BOOKS_API_KEY)

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8004
```

---

## Cómo ejecutar los tests

```bash
cd ai-enrichment-service

# Todos los tests
pytest tests/ -v

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v

# Con cobertura
pytest --cov=app --cov-report=term-missing

# Test específico
pytest tests/unit/test_normalizer.py::test_isbn10_converts_to_isbn13_correctly -v
```

### Tests obligatorios

**Servicio de enriquecimiento:**

| Test | Descripción |
|------|-------------|
| `test_enrich_by_isbn_google_books_success` | Flujo completo con Google Books |
| `test_enrich_fallback_when_google_fails` | Open Library como fallback |
| `test_enrich_all_sources_fail_returns_partial` | Respuesta parcial si todas fallan |
| `test_normalization_merges_fields_correctly` | Fusión de candidatos multi-fuente |
| `test_adapter_timeout_handled_gracefully` | Timeout no rompe el flujo |

**Módulo Normalizer:**

| Test | Descripción |
|------|-------------|
| `test_isbn10_converts_to_isbn13_correctly` | Conversión ISBN-10 a ISBN-13 |
| `test_invalid_isbn_raises_validation_error` | ISBN inválido lanza error |
| `test_author_format_single_name` | Formateo de un solo autor |
| `test_author_format_multiple_authors` | Formateo con varios autores |
| `test_title_normalization_removes_special_chars` | Limpieza de título |
| `test_source_merger_prefers_higher_confidence` | Fusión por confidence_score |
| `test_duplicate_detection_by_isbn` | Detección de duplicados |

---

## Modelos de dominio

### `EnrichmentRequest`
Solicitud de enriquecimiento recibida.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador de la solicitud |
| `book_id` | UUID | ID del libro en el catálogo |
| `isbn` | string | ISBN proporcionado (opcional) |
| `title` | string | Título proporcionado (opcional) |
| `author` | string | Autor proporcionado (opcional) |
| `publisher` | string | Editorial proporcionada (opcional) |
| `status` | enum | `pending`, `processing`, `completed`, `failed` |
| `requested_at` | datetime | Timestamp de la solicitud |
| `source_used` | enum | `google_books`, `open_library`, `crossref`, `none` |
| `error_message` | string | Mensaje si falló (nullable) |

### `EnrichmentResult`
Resultado normalizado persistido.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador del resultado |
| `request_id` | UUID | FK a `EnrichmentRequest` |
| `normalized_title` | string | Título normalizado |
| `normalized_author` | string | Autor en formato `Apellido, Nombre` |
| `normalized_publisher` | string | Editorial normalizada |
| `normalized_description` | string | Descripción normalizada |
| `cover_url` | string | URL de portada (nullable) |
| `confidence_score` | float | Confianza del resultado (0-1) |
| `created_at` | datetime | Timestamp de creación |

---

## Integración con otros servicios

- **No expone datos directamente a frontends** — todo pasa por el BFF (`http://localhost:8000`)
- **BFF rutas de admin:**
  - `GET /api/admin/enrichment/status` → este servicio
  - `POST /api/admin/enrichment/trigger` → este servicio
- Puede notificar a `catalog-service` con metadatos enriquecidos vía `CATALOG_SERVICE_URL`

---

## Migraciones Alembic

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones pendientes
alembic upgrade head

# Ver historial
alembic history

# Revertir última migración
alembic downgrade -1
```

Migraciones del Sprint 2:
- `001_create_enrichment_request.py`
- `002_create_enrichment_result.py`
## DEV 2 Contribution Notes

This contribution focuses on the normalization pipeline used in the AI Enrichment Service.

### Implemented responsibilities
- Metadata cleanup for titles and author names
- ISBN validation and ISBN-10 to ISBN-13 conversion
- Duplicate detection before persistence
- Multi-source merge strategy using confidence score

### Technical impact
These improvements ensure consistency across heterogeneous external APIs and reduce data redundancy in the enrichment workflow.

### Validation
Unit tests were added and executed for:
- ISBN conversion
- Author formatting
- Duplicate detection
- Source merging behavior