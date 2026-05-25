import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from app.domain.entities.interaction import AssistantInteraction
from app.domain.interfaces.interaction_repository import InteractionRepository
from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.inventory_client import InventoryClient
from app.infrastructure.clients.pricing_client import PricingClient


_PRICE_WORDS = (
    "precio", "precios", "cuesta", "costo", "vale", "valor",
    "cuánto", "cuanto", "barato", "baratos", "caro", "caros"
)

_STOCK_WORDS = (
    "disponible", "disponibles", "disponibilidad", "stock",
    "unidades", "existencias"
)

_HARDWARE_TERMS = (
    "monitor", "monitores", "pc", "computador", "computadora", "equipo",
    "gpu", "tarjeta", "tarjeta madre", "tarjeta grafica", "tarjeta gráfica",
    "placa madre", "motherboard", "procesador", "cpu", "memoria", "ram",
    "ssd", "hdd", "almacenamiento", "fuente", "psu", "refrigeración",
    "cooler", "aio", "ventilador", "periférico", "periferico", "componente",
    "repuesto", "hardware", "streaming",
)

_RECOMMEND_WORDS = (
    "recomienda", "recomendar", "recomiéndame", "recomiendame",
    "alternativa", "alternativas", "similar", "parecido", "sugerir",
    "sugerencias", "configuración", "setup", "armado", "ensamblar",
    "mejor opción", "mejor pc", "mejor computador"
)

_FEATURE_WORDS = (
    "características", "caracteristicas", "especificaciones", "especificacion", "detalles",
    "técnicas", "tecnicas", "ficha técnica", "ficha tecnica", "modelo",
    "marca", "gpu", "cpu", "ram", "ssd", "hdd", "almacenamiento",
    "velocidad", "cores", "núcleos", "nucleos", "frecuencia", "compatibilidad",
)

_LIST_WORDS = (
    "muéstrame", "muestrame", "mostrar", "lista", "listar",
    "qué pc", "que pc", "computador", "computadores", "pcs", "equipos",
    "monitores", "periféricos", "componentes", "repuestos",
    "productos", "hardware", "disponibles", "en stock"
)

_FILLER_WORDS = {
    "que", "qué", "cual", "cuál", "cuanto", "cuánto",
    "hay", "tienen", "tienes", "precio", "precios", "cuesta",
    "costo", "vale", "valor", "disponible", "disponibles",
    "disponibilidad", "stock", "caracteristicas", "características",
    "descripcion", "descripción", "del", "de", "la", "el", "los",
    "las", "un", "una", "unos", "unas", "producto", "productos",
    "por", "favor", "me", "puedes", "puede", "decir", "consultar",
    "buscar", "busca", "quiero", "necesito", "sobre", "y", "con",
    "para", "en", "al", "lo", "mi", "tu", "su", "se", "es",
    "son", "esta", "este", "estos", "estas", "muéstrame", "muestrame",
    "mostrar", "lista", "listar", "recomienda", "recomendar",
    "recomiéndame", "recomiendame"
}

_CATEGORY_SYNONYMS = {
    "pc": ["pc", "computador", "computadora", "equipo", "desktop", "computadores"],
    "computador": ["pc", "computador", "computadora", "equipo", "desktop"],
    "computadora": ["pc", "computador", "computadora", "equipo", "desktop"],
    "gaming": ["gaming", "gamer", "pc gamer", "computador gamer"],
    "procesador": ["procesador", "cpu", "intel", "amd"],
    "memoria": ["memoria", "ram", "ddr4", "ddr5"],
    "almacenamiento": ["ssd", "hdd", "disco", "unidad", "almacenamiento"],
    "gpu": ["gpu", "tarjeta de video", "tarjeta grafica", "grafica"],
    "tarjeta madre": ["tarjeta madre", "motherboard", "placa madre", "placa base"],
    "fuente": ["fuente", "psu", "fuente de poder"],
    "refrigeracion": ["refrigeracion", "refrigeración", "cooler", "aio", "ventilador"],
    "montaje": ["montaje", "ensamblado", "armado"],
    "soporte": ["soporte", "reparacion", "mantenimiento", "servicio"],
    "monitor": ["monitor", "pantalla", "display"],
    "hardware": [
        "hardware", "componente", "componentes", "pc", "computador",
        "procesador", "cpu", "memoria", "ram", "ssd", "hdd", "gpu",
        "monitor", "periferico", "perifericos", "tarjeta", "placa",
        "fuente", "cooler", "almacenamiento", "equipo", "teclado", "mouse",
    ],
}


def _has_hardware_terms(text: str) -> bool:
    q = _normalize(text)
    return any(term in q for term in _HARDWARE_TERMS)


def _has_new_product_terms(text: str) -> bool:
    q = _normalize(text)
    return any(word in q for word in ("nuevo", "nuevos", "nuevas", "novedad", "novedades"))


def _normalize(text: str | None) -> str:
    if not text:
        return ""

    text = text.lower().strip()
    text = text.replace("¿", "").replace("?", "")
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_terms(question: str) -> str:
    clean = _normalize(question)
    words = [
        w for w in clean.split()
        if w not in {_normalize(x) for x in _FILLER_WORDS} and len(w) > 1
    ]
    return " ".join(words).strip()


def _detect_intent(question: str) -> str:
    q = _normalize(question)

    wants_price = any(_normalize(w) in q for w in _PRICE_WORDS)
    wants_stock = any(_normalize(w) in q for w in _STOCK_WORDS)
    wants_features = any(_normalize(w) in q for w in _FEATURE_WORDS)
    wants_recommendation = any(_normalize(w) in q for w in _RECOMMEND_WORDS)
    wants_list = any(_normalize(w) in q for w in _LIST_WORDS)

    if "libros nuevos" in q or "nuevos libros" in q or "nuevos productos" in q or "novedades" in q or "recientes" in q or "esta semana" in q:
        return "catalog_list"

    if wants_recommendation:
        return "recommendation"

    if _has_hardware_terms(question) and _has_new_product_terms(question):
        return "catalog_list"

    if wants_list and wants_stock:
        return "available_books"

    if wants_list and wants_price:
        return "priced_books"

    if wants_list:
        return "catalog_list"

    if sum([wants_price, wants_stock, wants_features]) >= 2:
        return "commercial_query"

    if wants_price:
        return "pricing"

    if wants_stock:
        return "inventory"

    if wants_features:
        return "catalog"

    terms = _extract_terms(question)
    greeting_words = {"hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "gracias"}
    if q in greeting_words:
        return "general"

    if terms:
        return "catalog"

    return "general"


def _fmt_price(value: Any) -> str:
    if value in (None, "", [], {}):
        return "No registrado"

    try:
        amount = float(value)
        if amount.is_integer():
            return f"${amount:,.0f} COP".replace(",", ".")
        return f"${amount:,.2f} COP"
    except Exception:
        return str(value)


def _first_not_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _as_int(value: Any) -> int:
    try:
        if value in (None, "", [], {}):
            return 0
        return int(float(value))
    except Exception:
        return 0


def _field(book: dict, *names: str) -> Any:
    for name in names:
        if name in book and book.get(name) not in (None, "", [], {}):
            return book.get(name)
    return None


def _product_text(book: dict) -> str:
    values = [
        _field(book, "title", "name", "model"),
        _field(book, "author", "authors", "manufacturer", "brand"),
        _field(book, "category", "category_name", "genre"),
        _field(book, "publisher", "editorial", "brand", "manufacturer"),
        _field(book, "isbn", "sku", "model_number"),
        _field(book, "description", "summary", "synopsis", "details"),
    ]
    return _normalize(" ".join(str(v) for v in values if v))


def _title(book: dict) -> str:
    return str(_field(book, "title", "name", "model") or "Sin título")


def _author(book: dict) -> str:
    value = _field(book, "author", "authors", "manufacturer", "brand")
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value or "Marca no registrada")


def _category(book: dict) -> str:
    return str(_field(book, "category", "category_name", "genre") or "Categoría no registrada")


def _year(book: dict) -> str:
    return str(_field(book, "publication_year", "year", "released_year", "release_year") or "Año no registrado")


def _isbn(book: dict) -> str:
    return str(_field(book, "isbn", "ISBN", "sku", "model_number") or "Código no registrado")


def _publisher(book: dict) -> str:
    return str(_field(book, "publisher", "editorial", "brand", "manufacturer") or "Marca no registrada")


def _description(book: dict) -> str:
    return str(_field(book, "description", "summary", "synopsis", "details") or "Descripción no registrada")


def _condition(book: dict) -> str:
    return str(_field(book, "condition", "estado", "physical_condition") or "Condición no registrada")


def _local_quantity(book: dict) -> int:
    return _as_int(
        _field(
            book,
            "quantity_available",
            "available_quantity",
            "availability",
            "stock",
            "quantity",
            "available",
            "units",
        )
    )


def _local_price(book: dict) -> Any:
    return _field(
        book,
        "suggested_price",
        "price",
        "amount",
        "sale_price",
        "current_price",
        "precio",
    )


def _score_book(book: dict, terms: str) -> float:
    if not terms:
        return 0

    terms_norm = _normalize(terms)
    title_norm = _normalize(_title(book))
    author_norm = _normalize(_author(book))
    category_norm = _normalize(_category(book))
    isbn_norm = _normalize(_isbn(book))
    full_text = _product_text(book)

    score = 0.0

    if terms_norm == title_norm:
        score += 100

    if terms_norm in title_norm:
        score += 75

    if title_norm in terms_norm:
        score += 60

    for word in terms_norm.split():
        if word in title_norm:
            score += 15
        if word in author_norm:
            score += 8
        if word in category_norm:
            score += 8
        if word in isbn_norm:
            score += 20
        if word in full_text:
            score += 4

    score += SequenceMatcher(None, terms_norm, title_norm).ratio() * 35

    return score


def _category_terms_from_question(question: str) -> list[str]:
    q = _normalize(question)
    found: list[str] = []

    for key, values in _CATEGORY_SYNONYMS.items():
        key_norm = _normalize(key)
        if key_norm in q:
            found.extend([_normalize(v) for v in values])

    return list(dict.fromkeys(found))


class ChatUseCase:
    def __init__(
        self,
        repo: InteractionRepository,
        catalog: CatalogClient,
        pricing: PricingClient,
        inventory: InventoryClient,
    ) -> None:
        self._repo = repo
        self._catalog = catalog
        self._pricing = pricing
        self._inventory = inventory

    def execute(self, session_id: str, question: str) -> AssistantInteraction:
        intent = _detect_intent(question)
        answer = self._build_answer(intent, question)

        interaction = AssistantInteraction(
            session_id=session_id,
            user_question=question,
            interpreted_intent=intent,
            answer_text=answer,
        )
        return self._repo.save(interaction)
    
    def _answer_general(self) -> str:
        return (
            "Puedo ayudarte con información real del sistema sobre catálogo de hardware, "
            "disponibilidad, precios, repuestos y soporte técnico."
        )

    def _answer_hardware(self, question: str, intent: str) -> str:
        q = _normalize(question)

        if intent in ("recommendation", "catalog_list"):
            if "monitor" in q or "streaming" in q:
                return (
                    "No hay productos reales de hardware listados en el catálogo actual, "
                    "pero puedo recomendarte qué buscar para streaming: un monitor de 27\" IPS o 144Hz con baja latencia, "
                    "buena reproducción de color y una PC equilibrada con CPU de 6 a 8 núcleos y una GPU moderna."
                )

            if "pc" in q or "configuración" in q or "configuraciones" in q or "gaming" in q:
                return (
                    "En este catálogo no hay PCs de gaming reales disponibles, "
                    "pero una buena configuración para gaming incluye CPU Intel Core i5/i7 o AMD Ryzen 5/7, 16 GB de RAM, "
                    "GPU NVIDIA RTX 3060/4060 o superior, SSD de 1 TB, una fuente de calidad y buena refrigeración."
                )

            if "perif" in q or "teclado" in q or "ratón" in q or "auriculares" in q or "mouse" in q:
                return (
                    "No hay periféricos reales cargados en el catálogo actual, "
                    "pero puedo ayudarte a elegir un teclado, ratón, auriculares, monitor o accesorios según tu estilo de uso y presupuesto."
                )

            return (
                "No hay productos reales de hardware en el catálogo actual, "
                "pero puedo darte recomendaciones prácticas si me dices qué tipo de componente o equipo necesitas."
            )

        if intent == "inventory":
            return (
                "No tengo inventario de hardware real en este catálogo. "
                "Si buscas disponibilidad de componentes o periféricos, cuéntame qué tipo de producto necesitas y te oriento."
            )

        if intent == "pricing":
            return (
                "No hay precios reales de hardware en este catálogo. "
                "Los costos varían mucho según marca, modelo y disponibilidad, pero puedo darte rangos aproximados si me dices el componente."
            )

        if intent == "commercial_query":
            return (
                "No hay datos reales de hardware detallados en el catálogo actual. "
                "Dime qué componente o equipo te interesa y te sugiero una opción adecuada."
            )

        return (
            "Actualmente no hay hardware real cargado en este catálogo, "
            "pero puedo ayudarte a definir requisitos de CPU, GPU, RAM, almacenamiento, monitores o periféricos."
        )

    def _build_answer(self, intent: str, question: str) -> str:
        if intent == "commercial_query":
            return self._answer_commercial_query(question)

        if intent == "pricing":
            return self._answer_pricing(question)

        if intent == "inventory":
            return self._answer_inventory(question)

        if intent == "available_books":
            return self._answer_available_books(question)

        if intent == "priced_books":
            return self._answer_priced_books(question)

        if intent == "catalog_list":
            return self._answer_catalog_list(question)

        if intent == "recommendation":
            return self._answer_recommendation(question)

        if _has_hardware_terms(question):
            return self._answer_hardware(question, intent)

        if intent == "general":
            return self._answer_general()

        return self._answer_catalog(question)

    def _get_catalog_books(self, terms: str = "", limit: int = 30) -> list[dict]:
        if terms:
            try:
                response = self._catalog.search_books(terms, limit=limit) or []
            except Exception:
                response = []
            return response if isinstance(response, list) else []

        try:
            response = self._catalog.list_books(limit=limit) or []
        except Exception:
            response = []

        return response if isinstance(response, list) else []

    def _find_books(self, question: str, limit: int = 5) -> list[dict]:
        terms = _extract_terms(question)
        category_terms = _category_terms_from_question(question)

        books = self._get_catalog_books(terms=terms, limit=max(limit, 40))

        if not books and category_terms:
            for term in category_terms:
                books = self._get_catalog_books(terms=term, limit=max(limit, 40))
                if books:
                    break

        if not books and terms:
            for term in terms.split():
                books = self._get_catalog_books(terms=term, limit=max(limit, 40))
                if books:
                    break

        # Fallback amplio: lista todo el catálogo y filtra localmente
        if not books:
            all_books = self._get_catalog_books(limit=80)
            if all_books:
                if terms:
                    local_filtered = [
                        b for b in all_books
                        if any(t in _product_text(b) for t in terms.split())
                    ]
                    books = local_filtered if local_filtered else all_books
                elif category_terms:
                    local_filtered = [
                        b for b in all_books
                        if any(ct in _product_text(b) for ct in category_terms)
                    ]
                    books = local_filtered if local_filtered else all_books
                else:
                    books = all_books

        if not books:
            return []

        if terms:
            books = sorted(
                books,
                key=lambda book: _score_book(book, terms),
                reverse=True,
            )

            scored = [book for book in books if _score_book(book, terms) >= 18]
            if scored:
                books = scored

        if category_terms:
            filtered = [
                book for book in books
                if any(term in _product_text(book) for term in category_terms)
            ]
            if filtered:
                books = filtered

        return books[:limit]

    def _get_quantity(self, book: dict) -> int:
        quantity = _local_quantity(book)

        if quantity > 0:
            return quantity

        book_id = str(_field(book, "id", "book_id") or "")
        isbn = str(_field(book, "isbn", "ISBN") or "").replace("-", "").strip()

        availability = None

        if isbn:
            try:
                availability = self._inventory.get_availability(isbn)
            except Exception:
                availability = None

        if not availability and book_id:
            try:
                availability = self._inventory.get_availability(book_id)
            except Exception:
                availability = None

        if availability:
            quantity = _as_int(
                _field(
                    availability,
                    "quantity_available",
                    "available_quantity",
                    "stock",
                    "quantity",
                    "available",
                    "units",
                )
            )

        return quantity

    def _get_price(self, book: dict) -> Any:
        local_price = _local_price(book)

        if local_price not in (None, "", [], {}):
            return local_price

        book_id = str(_field(book, "id", "book_id") or "")

        if not book_id:
            return None

        try:
            price_data = self._pricing.get_price(book_id)
        except Exception:
            price_data = None

        if not price_data:
            return None

        return _first_not_empty(
            price_data.get("suggested_price"),
            price_data.get("price"),
            price_data.get("amount"),
            price_data.get("sale_price"),
            price_data.get("current_price"),
        )

    def _answer_commercial_query(self, question: str) -> str:
        books = self._find_books(question, limit=3)

        if not books:
            return (
                "No encontré un producto relacionado con tu consulta en el catálogo real. "
                "Para evitar inventar información, intenta escribir el nombre, marca o código exacto."
            )

        book = books[0]

        quantity = self._get_quantity(book)
        price = self._get_price(book)

        stock_text = (
            f"Disponible ({quantity} unidad(es))"
            if quantity > 0
            else "Sin stock registrado o no disponible"
        )

        return (
            f"Encontré información real del sistema para '{_title(book)}'.\n\n"
            f"Disponibilidad: {stock_text}.\n"
            f"Precio sugerido: {_fmt_price(price)}.\n"
            f"Marca: {_author(book)}.\n"
            f"Categoría: {_category(book)}.\n"
            f"Año: {_year(book)}.\n"
            f"Código: {_isbn(book)}.\n"
            f"Condición: {_condition(book)}.\n"
            f"Descripción: {_description(book)}\n\n"
            f"No inventé datos: si algún campo aparece como no registrado, significa que no está disponible en los servicios actuales."
        )

    def _answer_pricing(self, question: str) -> str:
        books = self._find_books(question, limit=5)

        if not books:
            return "No encontré ese producto en el catálogo real, por eso no puedo consultar un precio."

        book = books[0]
        price = self._get_price(book)

        if price in (None, "", [], {}):
            return (
                f"No tengo precio calculado para '{_title(book)}'. "
                f"En el catálogo aparece como: Precio a consultar."
            )

        return f"El precio sugerido de '{_title(book)}' es {_fmt_price(price)}."

    def _get_inventory_items(self, limit: int = 50) -> list[dict]:
        try:
            response = self._inventory.list_items(limit=limit)
        except TypeError:
            try:
                response = self._inventory.list_items()
            except Exception:
                response = []
        except Exception:
            response = []

        return response if isinstance(response, list) else []

    def _find_inventory_items(self, question: str, limit: int = 5) -> list[dict]:
        terms = _extract_terms(question)
        items = self._get_inventory_items(limit=50)

        if not items:
            return []

        if terms:
            items = sorted(items, key=lambda item: _score_book(item, terms), reverse=True)
            scored = [item for item in items if _score_book(item, terms) >= 18]
            if scored:
                items = scored

        return items[:limit]

    def _answer_inventory(self, question: str) -> str:
        books = self._find_books(question, limit=5)

        if not books:
            books = self._find_inventory_items(question, limit=5)

        if not books:
            return "No encontré ese producto en el catálogo real ni en inventario, por eso no puedo verificar disponibilidad."

        book = books[0]
        quantity = self._get_quantity(book)

        if quantity > 0:
            return f"'{_title(book)}' está disponible. Hay {quantity} unidad(es) registradas."

        return f"'{_title(book)}' aparece sin stock disponible en inventario."

    def _answer_catalog(self, question: str) -> str:
        books = self._find_books(question, limit=5)

        if not books:
            return (
                "No encontré productos relacionados en el catálogo real. "
                "Intenta escribir el modelo, marca, código o una categoría de hardware."
            )

        if len(books) == 1:
            book = books[0]
            return (
                f"Encontré este producto en el catálogo:\n"
                f"- {_title(book)} — {_author(book)} ({_year(book)})\n"
                f"Categoría: {_category(book)}.\n"
                f"Código: {_isbn(book)}."
            )

        lines = []
        for book in books[:5]:
            lines.append(f"- {_title(book)} — {_author(book)} ({_year(book)})")

        return "Encontré estos productos en el catálogo:\n" + "\n".join(lines)

    def _answer_available_books(self, question: str) -> str:
        books = self._find_books(question, limit=20)

        available = []
        for book in books:
            quantity = self._get_quantity(book)
            if quantity > 0:
                available.append((book, quantity))

        # Si el catálogo no reportó stock, consulta inventario directamente
        if not available:
            inventory_items = self._get_inventory_items(limit=80)
            terms = _extract_terms(question)
            if inventory_items and terms:
                inventory_items = sorted(
                    inventory_items,
                    key=lambda i: _score_book(i, terms),
                    reverse=True,
                )
                scored = [i for i in inventory_items if _score_book(i, terms) >= 8]
                if scored:
                    inventory_items = scored

            for item in inventory_items[:20]:
                quantity = _local_quantity(item)
                if quantity > 0:
                    available.append((item, quantity))

        # Productos con stock confirmado encontrados
        if available:
            lines = []
            for book, quantity in available[:5]:
                lines.append(f"- {_title(book)} — {_author(book)}: {quantity} unidad(es)")
            return "Estos productos aparecen con stock disponible:\n" + "\n".join(lines)

        # Fallback: muestra productos del catálogo aunque no tengan stock confirmado
        if books:
            lines = []
            for book in books[:5]:
                lines.append(f"- {_title(book)} — {_author(book)} (disponibilidad no confirmada)")
            return (
                "Encontré estos productos en el catálogo, pero no se pudo confirmar "
                "su stock en inventario en este momento:\n"
                + "\n".join(lines)
                + "\n\nVerifica con el área de inventario para disponibilidad exacta."
            )

        return (
            "No encontré productos relacionados con esa consulta en el catálogo. "
            "Intenta buscar por nombre de producto, categoría o marca específica."
        )

    def _answer_priced_books(self, question: str) -> str:
        books = self._find_books(question, limit=20)

        priced = []
        for book in books:
            price = self._get_price(book)
            if price not in (None, "", [], {}):
                priced.append((book, price))

        if not priced:
            return (
                "No encontré productos con precio registrado para esa consulta. "
                "En este momento varios productos pueden aparecer como 'Precio a consultar'."
            )

        lines = []
        for book, price in priced[:5]:
            lines.append(f"- {_title(book)} — {_fmt_price(price)}")

        return "Estos productos tienen precio registrado:\n" + "\n".join(lines)

    def _answer_catalog_list(self, question: str) -> str:
        books = self._find_books(question, limit=5)

        if not books:
            if _has_hardware_terms(question):
                return (
                    "No encontré productos de hardware relacionados con esa consulta. "
                    "Intenta buscar por marca, modelo, tipo de monitor o una categoría específica."
                )
            return (
                "No encontré productos relacionados con esa consulta. "
                "Intenta con una categoría como PC, componentes, repuestos o soporte técnico."
            )

        lines = []
        for book in books:
            quantity = self._get_quantity(book)
            stock_text = f"{quantity} unidad(es)" if quantity > 0 else "sin stock registrado"
            lines.append(f"- {_title(book)} — {_author(book)} ({stock_text})")

        return "Encontré estos productos en el catálogo real:\n" + "\n".join(lines)

    def _answer_recommendation(self, question: str) -> str:
        books = self._find_books(question, limit=10)

        if not books:
            return "No encontré recomendaciones disponibles en el catálogo real en este momento."

        available_books = []
        fallback_books = []

        for book in books:
            quantity = self._get_quantity(book)
            if quantity > 0:
                available_books.append((book, quantity))
            else:
                fallback_books.append(book)

        if available_books:
            lines = []
            for book, quantity in available_books[:5]:
                lines.append(f"- {_title(book)} — {_author(book)}: {quantity} unidad(es)")
            return "Te recomiendo estas opciones con stock disponible:\n" + "\n".join(lines)

        lines = []
        for book in fallback_books[:5]:
            lines.append(f"- {_title(book)} — {_author(book)}")

        return (
            "Encontré estas opciones en el catálogo, pero no tienen stock registrado:\n"
            + "\n".join(lines)
        )