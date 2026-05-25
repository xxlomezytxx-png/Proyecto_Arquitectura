# Tienda de Hardware IA

Plataforma inteligente de catálogo, precios competitivos y venta de hardware, repuestos y soporte técnico.

---

## Sprints

| Sprint | Estado | Descripción |
|--------|--------|-------------|
| Sprint 1 | Completado | Base arquitectónica: auth, inventory, catalog, BFF, frontends, calidad de datos |
| Sprint 2 | Completado | Motor de IA: pricing trazable, enriquecimiento real, catálogo enriquecido, UI de precios |
| Sprint 3 | Completado | Flujo comercial completo: carrito, pedidos, asistente IA, recomendaciones, auditoría |

---

## Arquitectura

```
Usuario
  └─► commercial-frontend  :3000   (catálogo, carrito, checkout)
  └─► admin-frontend        :3001   (panel admin + pricing + enriquecimiento)
         └─► bff-gateway    :8009   (API Gateway único)
               ├─► auth-service            :8001  → auth_db
               ├─► inventory-service       :8002  → inventory_db
               ├─► catalog-service         :8003  → catalog_db
               ├─► ai-enrichment-service   :8004  → enrichment_db
               ├─► pricing-service         :8005  → pricing_db
               ├─► ai-enrichment-mock      :8006  (sin DB)
               ├─► data-quality-module     :8007  (proxy inventario)
               ├─► config-module           :8008  → config_db
               ├─► order-service           :8010  → order_db
               ├─► ai-assistant-service    :8011  → assistant_db
               └─► recommendation-service  :8012  (sin DB propia)
```

---

## Inicio rápido

### Requisitos previos

- Docker Desktop instalado y corriendo
- Git

### Primera vez (setup completo)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Juan1202/Ebook-AiCommerce.git
cd <ruta-al-proyecto>

# 2. Crear el archivo de variables de entorno
cp .env.example .env
# Editar .env si tienes API keys (ver sección Variables de entorno)

# 3. Construir y levantar todo
docker compose up --build
```

Al iniciar, el `catalog-service` puebla automáticamente la base de datos con 18 libros de muestra.

### Actualizar desde git (si ya tienes el proyecto)

```bash
git pull origin main

# Limpiar volúmenes anteriores (obligatorio al actualizar esquemas de BD)
docker compose down -v --rmi all

docker compose up --build
```

> Si no limpias los volúmenes al actualizar, las bases de datos antiguas persisten
> con esquemas desactualizados y los servicios fallarán al iniciar.

### Levantar sin rebuild (veces siguientes)

```bash
docker compose up
```

---

## Variables de entorno

Copia `.env.example` como `.env`. Los servicios funcionan **sin API keys** usando fallbacks internos:

| Variable | Descripción | Sin key |
|----------|-------------|---------|
| `GOOGLE_BOOKS_API_KEY` | Google Books API (enriquecimiento) | Usa Open Library + Crossref |
| `EBAY_APP_ID` | eBay Browse API (referencias de precio) | Usa reglas internas de precio |

Las API keys opcionales mejoran la calidad de los resultados pero no son necesarias para correr el sistema.

---

## Puertos

| Servicio | Puerto | Docs |
|----------|--------|------|
| commercial-frontend | 3000 | http://localhost:3000 |
| admin-frontend | 3001 | http://localhost:3001 |
| auth-service | 8001 | http://localhost:8001/docs |
| inventory-service | 8002 | http://localhost:8002/docs |
| catalog-service | 8003 | http://localhost:8003/docs |
| ai-enrichment-service | 8004 | http://localhost:8004/docs |
| pricing-service | 8005 | http://localhost:8005/docs |
| ai-enrichment-mock | 8006 | http://localhost:8006/docs |
| data-quality-module | 8007 | http://localhost:8007/docs |
| config-module | 8008 | http://localhost:8008/docs |
| bff-gateway | 8009 | http://localhost:8009/docs |
| order-service | 8010 | http://localhost:8010/docs |
| ai-assistant-service | 8011 | http://localhost:8011/docs |
| recommendation-service | 8012 | http://localhost:8012/docs |

---

## Verificar que todo está corriendo

```bash
curl http://localhost:8009/health
```

---

## Flujos principales

### Sprint 1 — Inventario y catálogo base

**1. Obtener token de prueba:**
```bash
curl http://localhost:8009/api/auth/mock-token
```

**2. Cargar inventario:**
```bash
curl -X POST http://localhost:8009/api/inventory/upload \
  -F "file=@sample_inventory.csv"
```

**3. Ver inventario:**
```bash
curl http://localhost:8009/api/inventory/items
```

**4. Ver catálogo:**
```bash
curl http://localhost:8009/api/catalog/products
```

**5. Calidad de datos:**
```bash
curl http://localhost:8009/api/quality/summary
```

---

### Sprint 2 — Pricing e IA

**Calcular precio para un libro:**
```bash
curl -X POST http://localhost:8005/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "550e8400-e29b-41d4-a716-446655440001",
    "isbn": "9780141439518",
    "title": "Great Expectations",
    "condition": "BUENO",
    "publication_year": 2010
  }'
```

**Enriquecer un libro:**
```bash
curl -X POST http://localhost:8004/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "550e8400-e29b-41d4-a716-446655440001",
    "isbn": "9780141439518",
    "title": "Great Expectations",
    "author": "Charles Dickens"
  }'
```

**Ver precios vía BFF (admin):**
```bash
curl http://localhost:8009/api/admin/pricing/{book_id}
curl http://localhost:8009/api/admin/pricing/{book_id}/history
curl http://localhost:8009/api/admin/pricing/{book_id}/explanation
```

**Estado de APIs externas:**
```bash
curl http://localhost:8005/pricing/external-apis/status
curl http://localhost:8004/external-apis/status
```

---

### Sprint 3 — Pedidos y asistente IA

**Crear pedido:**
```bash
curl -X POST http://localhost:8009/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cliente-001",
    "items": [
      {"book_id": "550e8400-e29b-41d4-a716-446655440001", "quantity": 1}
    ]
  }'
```

**Consultar estado de un pedido:**
```bash
curl http://localhost:8009/api/orders/{order_id}
```

**Confirmar pedido:**
```bash
curl -X POST http://localhost:8009/api/orders/{order_id}/confirm
```

**Cancelar pedido:**
```bash
curl -X POST http://localhost:8009/api/orders/{order_id}/cancel
```

**Asistente IA — hacer una consulta:**
```bash
curl -X POST http://localhost:8009/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sesion-001",
    "question": "¿Qué libros de programación tienen disponibles?"
  }'
```

**Consulta de recomendaciones:**
```bash
curl http://localhost:8009/api/recommendations/{book_id}
```

**Auditoría del sistema:**
```bash
curl http://localhost:8009/api/audit/events
```

---

## Servicios

### Pricing Service (`pricing-service/`)

- Consulta **eBay Browse API** para referencias de precio de mercado
- Aplica factores de condición: NUEVO (1.0×), BUENO (0.75×), ACEPTABLE (0.50×), DETERIORADO (0.25×)
- **Fallback automático** con reglas internas si eBay no responde
- Circuit breaker tras 5 fallos consecutivos (cooldown 5 min)
- Toda decisión persiste con `explanation` en español

### AI Enrichment Service (`ai-enrichment-service/`)

- Consulta **Google Books → Open Library → Crossref** en orden de prioridad
- Normaliza autores a `Apellido, Nombre`, valida ISBN-10/13
- Circuit breaker independiente por cada API externa
- Si todas las fuentes fallan, devuelve datos parciales con `status: "failed"`

### Order Service (`order-service/`)

- Máquina de estados: `created → confirmed → cancelled`
- Valida disponibilidad de stock con Inventory Service antes de confirmar
- Registra el precio vigente al momento de creación del pedido
- No permite confirmar un pedido sin stock disponible

### AI Assistant Service (`ai-assistant-service/`)

- Detecta intención: búsqueda de libros, consulta de precios, disponibilidad, alternativas
- Consume Catalog, Pricing e Inventory **vía API** (sin acceso directo a BD ajena)
- No inventa precios ni disponibilidad — solo datos reales del sistema
- Persiste cada interacción en `assistant_db`

### Recommendation Service (`recommendation-service/`)

- Sugiere productos similares por categoría y características
- Sin persistencia propia — consulta Catalog Service en tiempo real

---

## Estructura del repositorio

```
<ruta-al-proyecto>/
├── admin-frontend/          # Panel administrativo (React)
├── commercial-frontend/     # Catálogo de ventas (React)
├── auth-service/            # Autenticación JWT (FastAPI)
├── inventory-service/       # Gestión de inventario (FastAPI)
├── catalog-service/         # Catálogo de productos (FastAPI)
├── ai-enrichment-service/   # Enriquecimiento IA real
├── ai-enrichment-mock/      # Mock enriquecimiento (Sprint 1)
├── pricing-service/         # Motor de precios
├── order-service/           # Gestión de pedidos
├── ai-assistant-service/    # Asistente IA conversacional
├── recommendation-service/  # Recomendaciones por similitud
├── bff-gateway/             # API Gateway (FastAPI)
├── data-quality-module/     # Módulo de calidad de datos
├── config-module/           # Configuración centralizada
├── seed/                    # Scripts de datos de muestra
├── docker-compose.yml       # Orquestación completa
├── .env.example             # Plantilla de variables de entorno
└── sample_inventory.csv     # Datos de prueba para inventario
```

---

## Desarrollo local (sin Docker)

```bash
# Cualquier servicio Python
cd <nombre-servicio> && pip install -r requirements.txt
uvicorn app.main:app --reload --port <puerto>

# Admin Frontend
cd admin-frontend && npm install && npm run dev    # → http://localhost:3001

# Commercial Frontend
cd commercial-frontend && npm install && npm run dev  # → http://localhost:3000
```

## Tests

```bash
# Por servicio Python
cd <nombre-servicio> && pytest tests/ -v --cov=app --cov-report=term-missing

# Admin Frontend
cd admin-frontend && npm test
```

---

## Tecnologías

- **Backend:** Python 3.11 + FastAPI + SQLAlchemy 2.x + PostgreSQL 15
- **Frontend:** React 18 + Vite
- **Arquitectura backend:** Hexagonal ligera (routers → application → domain → infrastructure)
- **Contenedores:** Docker + Docker Compose
- **Autenticación:** JWT (python-jose + passlib)
- **Validación:** Pydantic v2
- **HTTP entre servicios:** httpx con timeout y circuit breaker
- **APIs externas:** Google Books, Open Library, Crossref, eBay Browse API
