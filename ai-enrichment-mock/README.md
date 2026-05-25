# AI Enrichment Mock Service

## Propósito
Microservicio independiente para enriquecimiento de metadatos en la plataforma.

En Sprint 1 este servicio devuelve una respuesta mock para desacoplar desde el inicio la lógica de IA del resto del backend.

## Endpoints

### GET /enrichment/health
Permite verificar si el servicio está activo.

### POST /enrichment/enrich
Recibe datos básicos de un libro y devuelve metadata enriquecida mock.

#### Request ejemplo
```json
{
  "book_reference": "REF-001",
  "title": "Cien Años de Soledad",
  "author": "Gabriel García Márquez",
  "isbn": "978-0-06-088328-7"
}

#### Response ejemplo 
{
  "book_reference": "REF-001",
  "normalized_title": "Cien Años De Soledad",
  "normalized_author": "Gabriel García Márquez",
  "normalized_publisher": "Tusquets",
  "description": "Descripción enriquecida de 'Cien Años de Soledad' por Gabriel García Márquez. Publicado por Tusquets en 1981. Clasificado de forma mock en la categoría Tecnología para Sprint 1.",
  "category": "Tecnología",
  "keywords": ["tecnología", "innovación", "software", "cien", "gabriel"],
  "cover_url": "https://via.placeholder.com/200x300/4A90E2/FFFFFF?text=Cien+Años+de+So",
  "publication_year": 1981,
  "source_used": "mock_google_books",
  "confidence_score": 0.85,
  "metadata": {
    "isbn_verified": true,
    "sources_consulted": ["mock_google_books", "mock_open_library"],
    "sprint": "1 - mock data",
    "ready_for_real_ai": true
  }
}