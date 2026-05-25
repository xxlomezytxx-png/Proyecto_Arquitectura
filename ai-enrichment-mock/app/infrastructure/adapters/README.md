# Documentación Técnica - Dev 8 (Integración con APIs Externas)

**Desarrollador:** Santiago Waltero  
**Módulo:** `ai-enrichment-mock` (y componentes reutilizables)  
**Sprint:** 2

---

## 1. Resumen del Desarrollo

Se implementó una arquitectura de adaptadores para la integración con fuentes externas (Google Books, Open Library, Crossref, eBay) garantizando la robustez y la tolerancia a fallos del sistema. 

El objetivo principal fue cumplir la Historia de Usuario:
> *"Como sistema, quiero conectarme robustamente a fuentes externas para enriquecer y soportar pricing sin colapsar ante fallos."*

Para ello, se construyó un módulo centralizado bajo el patrón **Adapter**, inyectando capacidades de **Circuit Breaker** y **Caché en Memoria**, permitiendo que cualquier microservicio (como *Enrichment* o un futuro *Pricing*) pueda reutilizar este código base de forma desacoplada.

---

## 2. Arquitectura y Patrones

El código reside en `ai-enrichment-mock/app/infrastructure/adapters/`.

### 2.1. Circuit Breaker (`CircuitBreaker`)
Patrón diseñado para prevenir el colapso del sistema cuando una API externa está degradada o aplica bloqueos (Rate Limiting HTTP 429).
- **Estados:**
  - `CLOSED`: Las peticiones fluyen con normalidad hacia el servidor externo.
  - `OPEN`: El límite de fallos (`failure_threshold`) ha sido excedido. Las peticiones son rechazadas inmediatamente devolviendo un error `503 Service Unavailable`, ahorrando tiempo y peticiones en red.
  - `HALF_OPEN`: Tras pasar el tiempo de espera (`cooldown_seconds`), se permite una petición de prueba. Si es exitosa, se vuelve a `CLOSED`; si falla, regresa a `OPEN`.

### 2.2. Caché en Memoria (`SimpleCache`)
Sistema de clave-valor que intercepta las consultas repetidas.
- **Normalización:** Las claves de búsqueda se estandarizan (ej. eliminando espacios y forzando minúsculas) para maximizar la efectividad del caché (`normalize_key`).
- **TTL (Time to Live):** Los datos almacenados tienen tiempo de vida limitado según la configuración de cada proveedor, evitando datos estáticos u obsoletos de precios e inventarios.

### 2.3. Base Adapter (`BaseAdapter`)
Clase abstracta de la cual heredan todos los clientes externos. Centraliza el uso de la librería `requests` y se encarga del manejo genérico de excepciones.

---

## 3. Adaptadores Implementados

| Adaptador | Base URL | Threshold (Fallos) | Cooldown (Segundos) | TTL Caché | TimeOut |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Books** | `https://www.googleapis.com/books/v1` | 3 | 30s | 1h | 5s |
| **Open Library** | `https://openlibrary.org` | 3 | 45s | 2h | 5s |
| **Crossref** | `https://api.crossref.org` | 3 | 60s | 24h | 10s |
| **eBay** | `https://svcs.ebay.com/services/...` | 5 | 60s | 30 min | 5s |

---

## 4. Endpoints Expuestos para Monitoreo

Se creó un enrutador en FastAPI dedicado a la gestión de los adaptadores: `adapters_router.py`.

* **`GET /adapters/status`**
  Retorna un volcado del estado actual en tiempo real de todos los adaptadores. Útil para métricas, monitoreo y Health-Checks de la salud de comunicación con proveedores externos.

---

## 5. Pruebas Unitarias y Funcionales

Se incluyeron pruebas robustas usando `pytest` y `requests-mock` en el archivo `tests/test_adapters.py`.

### Casos de uso cubiertos (6/6 exitosos):
1. `test_cache_hit`: Valida que la segunda llamada no salga a red.
2. `test_404_handling`: Verifica el comportamiento pacífico ante recursos no encontrados.
3. `test_429_rate_limit_handling`: Asegura que el estado 429 sume un fallo y no rompa el código.
4. `test_consecutive_failures_open_circuit`: Garantiza la apertura del circuito (Raise Exception).
5. `test_circuit_recovery_after_cooldown`: Simula el tiempo de espera y comprueba el reinicio a Half-Open.
6. `test_cache_expiration`: Verifica la limpieza del caché una vez superado el TTL.

Para correr las pruebas localmente:
```bash
python -m pytest tests/test_adapters.py
```

---

## 6. Pruebas End-to-End (Postman)

Se entrega junto al proyecto el archivo **`Postman_Dev8_Adapters.json`** en la carpeta raíz.  
Esta colección contiene escenarios pre-configurados para demostrar en vivo a los evaluadores:
- El llenado del Caché usando la API de Open Library.
- La simulación del Circuit Breaker usando la API de Google Books hasta provocar intencionalmente un `503 Service Unavailable`, visualizando la protección del sistema.