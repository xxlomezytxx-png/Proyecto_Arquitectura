# BFF Gateway — Dev6 BFF Avanzado

## Descripción del proyecto

Este proyecto implementa un Backend For Frontend (BFF) para centralizar y optimizar la comunicación entre el frontend y los microservicios del sistema comercial.

El BFF actúa como una capa de orquestación encargada de:

- Agregar respuestas de múltiples microservicios
- Reducir llamadas innecesarias desde frontend
- Centralizar manejo de errores
- Exponer endpoints unificados
- Gestionar flujo comercial completo
- Integrar servicios de IA y pedidos

---

# Arquitectura del sistema

```txt
Frontend
   |
   v
BFF Gateway :3000
   |
   |---- Catalog Service :3001
   |---- Inventory Service :3002
   |---- Pricing Service :3003
   |---- Order Service :3004
   |---- AI Assistant Service :3005
   |---- Cart Service :3006
```

---

# Tecnologías utilizadas

- Node.js
- Express.js
- Axios
- Swagger/OpenAPI
- REST APIs
- JavaScript
- Postman

---

# Estructura del proyecto

```txt
bff-gateway/
│
├── src/
│   ├── controllers/
│   ├── services/
│   ├── routes/
│   ├── middlewares/
│   ├── docs/
│   ├── config/
│   ├── utils/
│   └── app.js
│
├── .env
├── server.js
├── package.json
└── README.md
```

---

# Variables de entorno

Crear archivo `.env`:

```env
PORT=3000

CATALOG_SERVICE=http://localhost:3001
INVENTORY_SERVICE=http://localhost:3002
PRICING_SERVICE=http://localhost:3003
ORDER_SERVICE=http://localhost:3004
AI_SERVICE=http://localhost:3005
ASSISTANT_SERVICE_URL=http://ai-assistant-service:8011
```

---

# Instalación

## Clonar proyecto

```bash
git clone <repository-url>
```

## Instalar dependencias

```bash
npm install
```

## Ejecutar servidor

```bash
node server.js
```

---

# Microservicios mock

| Servicio | Puerto |
|---|---|
| Catalog Service | 3001 |
| Inventory Service | 3002 |
| Pricing Service | 3003 |
| Order Service | 3004 |
| AI Assistant Service | 3005 |
| Cart Service | 3006 |

---

# Endpoints principales

## Products

### Obtener producto completo

```http
GET /api/products/{id}
```

---

## Orders

### Crear pedido

```http
POST /api/orders
```

---

## Cart

### Obtener carrito

```http
GET /api/cart
```

### Agregar al carrito

```http
POST /api/cart
```

### Eliminar del carrito

```http
DELETE /api/cart/{bookId}
```

---

## Assistant

### Consultar asistente IA

```http
POST /api/assistant/ask
```

---

## Health Check

### Estado de servicios

```http
GET /health
```

---

# Swagger/OpenAPI

La documentación Swagger se encuentra disponible en:

```txt
http://localhost:3000/api-docs
```

---

# Manejo de errores

El sistema implementa un middleware centralizado para el manejo de errores internos.

Archivo:

```txt
src/middlewares/errorHandler.js
```

---

# Características implementadas

- Gateway BFF centralizado
- Agregación de microservicios
- Integración de carrito
- Integración de pedidos
- Integración de AI Assistant
- Health check consolidado
- Manejo centralizado de errores
- Swagger/OpenAPI
- Arquitectura REST
- Integración distribuida

---

# Pruebas realizadas

Se realizaron pruebas mediante Postman para:

- Consulta de libros
- Creación de pedidos
- Gestión de carrito
- Consultas al AI Assistant
- Health check consolidado
- Validación de respuestas JSON
- Manejo de errores

---