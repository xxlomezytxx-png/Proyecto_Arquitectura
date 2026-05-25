# Auth Service — Tienda de Hardware IA

Microservicio de **autenticación y autorización** basado en JWT para la plataforma BookFlow.  
Puerto: **8001** | Stack: **Python 3.11 + FastAPI + SQLAlchemy + PostgreSQL**

---

## Arquitectura

El servicio sigue la **Arquitectura Hexagonal (Ports & Adapters)** con separación clara de capas, según lo exige el documento del proyecto:

```
auth-service/
├── app/
│   ├── routers/          # Capa de exposición (recibe requests HTTP)
│   │   └── auth_router.py
│   ├── application/      # Casos de uso (orquesta lógica de negocio)
│   │   └── auth_use_cases.py
│   ├── domain/           # Entidades y reglas de dominio
│   │   └── user.py
│   ├── infrastructure/   # Adaptadores de salida (BD, repositorios)
│   │   ├── database.py
│   │   └── user_repository.py
│   ├── config.py         # Configuración centralizada (Pydantic Settings)
│   └── main.py           # Punto de entrada FastAPI
├── tests/
│   └── test_auth.py      # Tests unitarios (pytest)
├── verify_auth.py        # Script de verificación E2E completo
├── BookFlow_Auth_Collection.json  # Colección Postman
├── Dockerfile
└── requirements.txt
```

---

## Endpoints

| Método | Ruta               | Descripción                          | Auth |
|--------|---------------------|--------------------------------------|------|
| POST   | `/auth/register`    | Registrar un nuevo usuario           | No   |
| POST   | `/auth/login`       | Iniciar sesión → Recibe dobje JWT    | No   |
| POST   | `/auth/refresh`     | Refrescar el access token            | No   |
| POST   | `/auth/logout`      | Revoca/invalida la sesión actual     | Sí (Bearer Token) |
| GET    | `/auth/verify`      | Verificar token (y blacklist)        | Sí (Bearer Token) |
| GET    | `/auth/mock-token`  | Token admin de prueba (solo dev)     | No   |
| GET    | `/health`           | Health check del servicio            | No   |

### Detalle de Endpoints

#### POST `/auth/register`
Registra un nuevo usuario. Si no se especifica el rol, se asigna `"user"` por defecto.  
**Nota:** El frontend comercial NO debe permitir registro de administradores. Solo vía API directa o Postman.

```json
// Request Body
{
  "username": "juan123",
  "email": "juan@bookflow.com",
  "password": "miPassword123",
  "role": "user"     // Opcional. Default: "user". Valores: "user" | "admin"
}
// Response 201
{
  "message": "Usuario registrado",
  "username": "juan123",
  "role": "user"
}
// Error 400 (usuario duplicado)
{ "detail": "El usuario ya existe" }
// Error 400 (email duplicado)
{ "detail": "El email ya está registrado" }
```

#### POST `/auth/login`
Autentica al usuario y genera un Action de doble JWT (un `access_token` temporal y un `refresh_token` duradero). Funciona para **todos los roles** (user y admin).

```
// Request: application/x-www-form-urlencoded
username=juan123&password=miPassword123

// Response 200
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "role": "user"
}
// Error 401
{ "detail": "Credenciales incorrectas" }
```

#### POST `/auth/refresh`
Toma el refresh_token provisto y, si aún es válido y no está revocado, emite un nuevo `access_token` fresco por 15 minutos.

```json
// Request Body
{
  "refresh_token": "eyJhbGci..."
}

// Response 200
{
  "access_token": "eyJhbGciN...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "role": "user"
}
```

#### POST `/auth/logout`
Ingresa el identificador único del token JWT (`jti`) en la base de datos de "Blacklist", revocando permanentemente su uso para que sea rechazado en endpoints protegidos.

```
// Header: Authorization: Bearer <token>

// Response 200
{
  "message": "Sesión cerrada correctamente"
}
```

#### GET `/auth/verify` (Endpoint Protegido)
Valida el token JWT y retorna la información del usuario. Si no se envía token o es inválido/expirado, responde `401`.

```
// Header: Authorization: Bearer <token>

// Response 200
{
  "username": "juan123",
  "role": "user",
  "user_id": 1
}
// Error 401 (sin token, inválido o expirado)
{ "detail": "Token inválido o expirado" }
```

---

## Criterios de Aceptación — Sprint 1

Según el documento **SPRINT_1_COMPLETO.pdf** (DEV 1 — AUTH / SEGURIDAD):

| # | Criterio de Aceptación (Documento) | Estado | Implementación |
|---|-------------------------------------|--------|----------------|
| 1 | Si credenciales correctas → genera JWT | ✅ | `POST /auth/login` → `TokenResponse` |
| 2 | Si credenciales incorrectas → error | ✅ | Responde HTTP 401 |
| 3 | Endpoint protegido sin token → 401 | ✅ | `GET /auth/verify` sin Bearer → 401 |
| 4 | Token inválido o expirado → 401 | ✅ | Validación JWT con `python-jose` |
| 5 | El servicio funciona de manera independiente | ✅ | Contenedor Docker propio + auth_db |

### Entregables Requeridos (SPRINT_1_COMPLETO.pdf)

| Entregable | Estado | Detalle |
|------------|--------|---------|
| Microservicio Auth funcionando | ✅ | FastAPI en puerto 8001 |
| Endpoint POST /login | ✅ | `/auth/login` con OAuth2PasswordRequestForm |
| Generación de JWT | ✅ | HS256 con `python-jose`, incluye `sub`, `role`, `user_id`, `exp` |
| Validación de JWT | ✅ | `/auth/verify` decodifica y valida |
| Endpoint protegido de prueba | ✅ | `/auth/verify` requiere `Bearer` token |
| Base de datos auth_db | ✅ | PostgreSQL con tabla `users` |
| Login correcto → devuelve token | ✅ | Verificado via Postman y script |
| Login incorrecto → error | ✅ | HTTP 401 "Credenciales incorrectas" |
| Endpoint sin token → 401 | ✅ | OAuth2PasswordBearer rechaza sin header |
| Endpoint con token → OK | ✅ | Retorna username, role, user_id |

### Mejoras Implementadas (de la Evaluación Sprint 1)

| Mejora Sugerida | Estado | Detalle |
|-----------------|--------|---------|
| Implementar roles y autorización | ✅ | Enum `UserRole(admin, user)` en modelo y JWT payload |
| Registro con rol por defecto | ✅ | `role: str = "user"` en `RegisterRequest` |

### Mejoras de Seguridad (Feedback Profesora - Incluidas en Sprint 1)

| Mejora | Estado |
|--------|--------|
| Refresh Tokens | ✅ (Doble Token JTI) |
| Invalidación de sesiones | ✅ (DB Blacklist) |

---

## Documentación Técnica (Requerida por SPRINT_1_COMPLETO.pdf)

### Qué hace el servicio
Servicio de autenticación JWT que permite registrar usuarios, iniciar sesión, y verificar tokens. Gestiona roles (`admin`/`user`) y protege endpoints mediante `OAuth2PasswordBearer`.

### Estructura del proyecto
Arquitectura Hexagonal: `routers/` → `application/` → `domain/` → `infrastructure/`

### Decisiones técnicas
- **BCrypt** para hashing de contraseñas (via `passlib` + `bcrypt==3.2.2`)
- **JWT HS256** para tokens (via `python-jose`)
- **Pydantic** para validación de payloads
- **SQLAlchemy** ORM con PostgreSQL aislado (`auth_db`)
- **OAuth2PasswordRequestForm** para login (estándar FastAPI/OAuth2)
- Rol por defecto `"user"` si no se especifica en el registro
---

## Seguridad (Sección 18 del documento maestro)

| Requisito del Documento | Estado |
|-------------------------|--------|
| Autenticación con JWT | ✅ |
| Hash de contraseñas (BCrypt) | ✅ |
| Roles y control de permisos | ✅ |
| Validación de payloads con Pydantic | ✅ |
| Manejo seguro de variables de entorno | ✅ (Pydantic Settings + .env) |
| CORS controlado | ✅ |

---

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión PostgreSQL | `postgresql://bookflow:bookflow123@auth-db:5432/auth_db` |
| `SECRET_KEY` | Clave para firmar JWT | `bookflow-secret-key-sprint1-development-only` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token normal | `15` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Expiración del comodín de renovación | `1440` (24 hr) |

---

## Modelo de Datos

### Tabla `users`
| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | Integer | PK, Auto-increment |
| `username` | String(100) | Unique, Not Null, Indexed |
| `email` | String(200) | Unique, Not Null, Indexed |
| `hashed_password` | String(255) | Not Null |
| `role` | Enum(`admin`, `user`) | Not Null, Default: `user` |
| `is_active` | Boolean | Default: True |
| `created_at` | DateTime | Auto (UTC) |

### Tabla `revoked_tokens` (Blacklist)
| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | Integer | PK, Auto-increment |
| `jti` | String(50) | Unique, Not Null, Indexed |
| `revoked_at` | DateTime | Auto (UTC) |

---

## Ejecución

### Con Docker (Recomendado)
```bash
# Desde la raíz del proyecto
docker-compose up -d auth-db auth-service
```

### Local
```bash
cd auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### A través del BFF Gateway
```bash
# Registro (rol por defecto: user)
curl -X POST http://localhost:8009/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass123"}'

# Registro de admin (solo via API/Postman, NO desde frontend)
curl -X POST http://localhost:8009/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","email":"admin@test.com","password":"pass123","role":"admin"}'

# Login (funciona para todos los roles)
curl -X POST http://localhost:8009/api/auth/login \
  -d "username=test&password=pass123"

# Verificar token
curl http://localhost:8009/api/auth/verify \
  -H "Authorization: Bearer <token>"
```

---

## Tests y Evidencias

### Tests Unitarios
```bash
pytest tests/test_auth.py -v
```
Incluye: health check, mock token, verificación de token, token inválido.

### Script de Verificación Completa
```bash
python verify_auth.py
```
Ejecuta flujo completo: Health → Register → Register (Admin) → Login → Verify → Mock Token → Verify Mock → Refresh Token → Verify Transitorio → Logout Token → Error 401 Rechazo.
```
la ejecucion se recomienda mediante docker, usa el siguiente comando
```bash
docker compose exec auth-service python verify_auth.py
```

### Colección Postman
Importar `BookFlow_Auth_Collection.json` en Postman para probar todos los endpoints manualmente.

---

## Dependencias

| Paquete | Versión | Uso |
|---------|---------|-----|
| `fastapi` | 0.111.0 | Framework web |
| `uvicorn` | 0.29.0 | Servidor ASGI |
| `sqlalchemy` | 2.0.30 | ORM |
| `psycopg2-binary` | 2.9.9 | Driver PostgreSQL |
| `pydantic` | 2.7.1 | Validación de datos |
| `pydantic-settings` | 2.2.1 | Configuración |
| `python-jose` | 3.3.0 | JWT |
| `passlib` | 1.7.4 | Hashing passwords |
| `bcrypt` | 3.2.2 | Backend BCrypt (pinned para compatibilidad) |
| `python-multipart` | 0.0.9 | Form data parsing |

> **Nota**: `bcrypt` está fijado a `3.2.2` para compatibilidad con `passlib 1.7.4`. Versiones 4.0+ causan errores en el hash de contraseñas.
