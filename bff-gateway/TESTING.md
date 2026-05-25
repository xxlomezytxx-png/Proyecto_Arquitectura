# Testing Documentation — BFF Gateway

## Objetivo

Validar el correcto funcionamiento del BFF Gateway y la integración con los microservicios del sistema comercial.

---

# Pruebas funcionales realizadas

| Prueba | Endpoint | Resultado |
|---|---|---|
| Consulta de producto | GET /api/products/1 | Exitosa |
| Crear pedido | POST /api/orders | Exitosa |
| Obtener carrito | GET /api/cart | Exitosa |
| Agregar al carrito | POST /api/cart | Exitosa |
| Eliminar del carrito | DELETE /api/cart/1 | Exitosa |
| Consulta AI Assistant | POST /api/assistant/ask | Exitosa |
| Health check | GET /health | Exitosa |

---

# Casos de fallo demostrados

## Fallo de Inventory Service

### Escenario

El microservicio Inventory Service fue detenido manualmente.

### Resultado esperado

El BFF responde error controlado:

```json
{
  "success": false,
  "message": "Error consuming microservices"
}
```

### Resultado obtenido

El sistema respondió correctamente usando middleware centralizado de errores.

---

## Fallo de AI Assistant Service

### Escenario

El AI Assistant Service fue detenido manualmente.

### Resultado esperado

```json
{
  "success": false,
  "message": "Error communicating with AI Assistant"
}
```

### Resultado obtenido

El BFF manejó correctamente el fallo y devolvió respuesta controlada.

---

# Herramientas utilizadas

- Postman
- Node.js
- Express.js
- Swagger UI

---

# Conclusiones

El sistema implementa correctamente:

- Integración distribuida
- Comunicación entre microservicios
- Manejo centralizado de errores
- Respuestas agregadas
- Validación de endpoints
- Health checks consolidados