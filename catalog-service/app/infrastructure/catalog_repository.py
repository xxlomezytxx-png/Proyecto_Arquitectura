from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.book import Book, Category
from app.infrastructure.database import BookModel, CategoryModel

_DEFAULT_CATEGORIES = [
    "Gaming PCs",
    "Gaming Laptops",
    "GPUs",
    "Processors",
    "Motherboards",
    "RAM",
    "Storage",
    "Cooling",
    "Monitors",
    "Peripherals",
    "Power Supplies",
    "Cases",
    "Services",
]


def _book(m: BookModel) -> Book:
    return Book(
        id=m.id,
        title=m.title,
        subtitle=m.subtitle,
        author=m.author,
        publisher=m.publisher,
        publication_year=m.publication_year,
        volume=m.volume,
        isbn=m.isbn,
        issn=m.issn,
        category_id=m.category_id,
        description=m.description,
        cover_url=m.cover_url,
        price=m.price,
        condition=m.condition,
        stock=m.stock,
        enriched_flag=m.enriched_flag,
        published_flag=m.published_flag,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _cat(m: CategoryModel) -> Category:
    return Category(id=m.id, name=m.name, description=m.description)


_DEFAULT_BOOKS = [
    {
        "title": "ASUS ROG Strix Gaming PC",
        "author": "ASUS",
        "publisher": "ROG Strix",
        "isbn": "sku:rog-strix-pc-001",
        "category_name": "Gaming PCs",
        "price": 6800000,
        "condition": "NUEVO",
        "stock": 5,
        "description": "Sistema gaming listo para 4K con Intel Core i9, RTX 4080 y refrigeración líquida.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "MSI Aegis Ti5 Gaming PC",
        "author": "MSI",
        "publisher": "Aegis Ti5",
        "isbn": "sku:msi-aegis-ti5-002",
        "category_name": "Gaming PCs",
        "price": 7200000,
        "condition": "BUENO",
        "stock": 3,
        "description": "Torre gamer de alto rendimiento con RTX 4080 Super y SSD NVMe de 2TB.",
        "cover_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "ASUS ROG Flow X16",
        "author": "ASUS",
        "publisher": "ROG",
        "isbn": "sku:flow-x16-003",
        "category_name": "Gaming Laptops",
        "price": 5200000,
        "condition": "NUEVO",
        "stock": 4,
        "description": "Laptop convertible gamer con pantalla de 16 pulgadas, CPU Intel y GPU RTX para creación y juego.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Dell Alienware x16",
        "author": "Dell",
        "publisher": "Alienware",
        "isbn": "sku:alienware-x16-004",
        "category_name": "Gaming Laptops",
        "price": 5990000,
        "condition": "BUENO",
        "stock": 2,
        "description": "Laptop premium gaming con pantalla QHD y teclado RGB personalizable.",
        "cover_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "NVIDIA GeForce RTX 4080",
        "author": "NVIDIA",
        "publisher": "GeForce",
        "isbn": "sku:rtx-4080-005",
        "category_name": "GPUs",
        "price": 7400000,
        "condition": "NUEVO",
        "stock": 7,
        "description": "Tarjeta gráfica de gama alta para 4K y renderización multimedia intensiva.",
        "cover_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "AMD Radeon RX 7900 XT",
        "author": "AMD",
        "publisher": "Radeon",
        "isbn": "sku:rx-7900-006",
        "category_name": "GPUs",
        "price": 6500000,
        "condition": "BUENO",
        "stock": 5,
        "description": "GPU para gaming de alto rendimiento con ray tracing y altas frecuencias.",
        "cover_url": "https://images.unsplash.com/photo-1591799265444-d66432b91588?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Intel Core i9-14900K",
        "author": "Intel",
        "publisher": "Core i9",
        "isbn": "sku:i9-14900k-007",
        "category_name": "Processors",
        "price": 1450000,
        "condition": "NUEVO",
        "stock": 9,
        "description": "Procesador Intel de última generación para gaming y creación de contenido.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "AMD Ryzen 9 7950X",
        "author": "AMD",
        "publisher": "Ryzen",
        "isbn": "sku:ryzen-7950x-008",
        "category_name": "Processors",
        "price": 1390000,
        "condition": "NUEVO",
        "stock": 8,
        "description": "Procesador AMD de alto rendimiento para estaciones de trabajo y juegos.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "ASUS ROG Strix Z790-E",
        "author": "ASUS",
        "publisher": "ROG Strix",
        "isbn": "sku:strix-z790-009",
        "category_name": "Motherboards",
        "price": 1390000,
        "condition": "BUENO",
        "stock": 6,
        "description": "Placa base para CPUs Intel con soporte DDR5 y conectividad avanzada.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "MSI MPG B650 Carbon",
        "author": "MSI",
        "publisher": "B650 Carbon",
        "isbn": "sku:b650-carbon-010",
        "category_name": "Motherboards",
        "price": 1240000,
        "condition": "BUENO",
        "stock": 5,
        "description": "Placa base AMD con diseño premium y soporte para DDR5.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Corsair Vengeance DDR5 32GB",
        "author": "Corsair",
        "publisher": "Vengeance",
        "isbn": "sku:ddr5-32gb-011",
        "category_name": "RAM",
        "price": 820000,
        "condition": "NUEVO",
        "stock": 12,
        "description": "Memoria DDR5 de 32GB para gaming y rendimiento profesional.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "G.Skill Trident Z5 RGB 32GB",
        "author": "G.Skill",
        "publisher": "Trident Z5",
        "isbn": "sku:trident-z5-012",
        "category_name": "RAM",
        "price": 840000,
        "condition": "BUENO",
        "stock": 7,
        "description": "Memoria RAM DDR5 con iluminación RGB y frecuencia elevada.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Samsung 990 Pro 2TB",
        "author": "Samsung",
        "publisher": "990 Pro",
        "isbn": "sku:990-pro-2tb-013",
        "category_name": "Storage",
        "price": 760000,
        "condition": "NUEVO",
        "stock": 10,
        "description": "SSD NVMe de alto rendimiento para cargas rápidas y gran capacidad.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "WD Black SN850X 2TB",
        "author": "Western Digital",
        "publisher": "Black",
        "isbn": "sku:sn850x-2tb-014",
        "category_name": "Storage",
        "price": 720000,
        "condition": "BUENO",
        "stock": 8,
        "description": "SSD PCIe 4.0 con latencias bajas para gaming y edición.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Corsair iCUE H150i Elite",
        "author": "Corsair",
        "publisher": "iCUE",
        "isbn": "sku:h150i-015",
        "category_name": "Cooling",
        "price": 780000,
        "condition": "BUENO",
        "stock": 9,
        "description": "Enfriamiento líquido AIO para sistemas gaming de alto rendimiento.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Noctua NH-D15",
        "author": "Noctua",
        "publisher": "NH-D15",
        "isbn": "sku:nh-d15-016",
        "category_name": "Cooling",
        "price": 420000,
        "condition": "BUENO",
        "stock": 11,
        "description": "Disipador de aire de alto rendimiento para CPUs potentes.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Samsung Odyssey G7 27\"",
        "author": "Samsung",
        "publisher": "Odyssey",
        "isbn": "sku:odyssey-g7-017",
        "category_name": "Monitors",
        "price": 1850000,
        "condition": "BUENO",
        "stock": 6,
        "description": "Monitor curvo gaming de 27 pulgadas con alta tasa de refresco y QHD.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "LG UltraGear 34\"",
        "author": "LG",
        "publisher": "UltraGear",
        "isbn": "sku:ultragear-34-018",
        "category_name": "Monitors",
        "price": 2490000,
        "condition": "NUEVO",
        "stock": 4,
        "description": "Monitor ultrawide 34 pulgadas para gaming y productividad.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Razer BlackWidow V4 Pro",
        "author": "Razer",
        "publisher": "BlackWidow",
        "isbn": "sku:blackwidow-v4-019",
        "category_name": "Peripherals",
        "price": 790000,
        "condition": "BUENO",
        "stock": 12,
        "description": "Teclado mecánico gamer con switches ópticos y retroiluminación.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Logitech G502 X",
        "author": "Logitech",
        "publisher": "G502",
        "isbn": "sku:g502x-020",
        "category_name": "Peripherals",
        "price": 320000,
        "condition": "NUEVO",
        "stock": 15,
        "description": "Mouse gaming de alta precisión con peso ajustable.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Corsair RM850x 850W",
        "author": "Corsair",
        "publisher": "RMx",
        "isbn": "sku:rm850x-021",
        "category_name": "Power Supplies",
        "price": 650000,
        "condition": "NUEVO",
        "stock": 14,
        "description": "Fuente de poder 850W 80 Plus Gold para sistemas gaming avanzados.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Seasonic Focus GX-750",
        "author": "Seasonic",
        "publisher": "Focus GX",
        "isbn": "sku:focus-gx-022",
        "category_name": "Power Supplies",
        "price": 590000,
        "condition": "BUENO",
        "stock": 10,
        "description": "Fuente de poder modular 750W con certificación 80 Plus Gold.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "NZXT H510",
        "author": "NZXT",
        "publisher": "H510",
        "isbn": "sku:h510-023",
        "category_name": "Cases",
        "price": 320000,
        "condition": "BUENO",
        "stock": 11,
        "description": "Gabinete compacto con excelente gestión de cables y flujo de aire.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Lian Li Lancool II",
        "author": "Lian Li",
        "publisher": "Lancool",
        "isbn": "sku:lancool-ii-024",
        "category_name": "Cases",
        "price": 420000,
        "condition": "BUENO",
        "stock": 8,
        "description": "Gabinete con panel lateral de vidrio templado y refrigeración optimizada.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Servicio armado PC gaming",
        "author": "TechFlow",
        "publisher": "TechFlow Servicios",
        "isbn": "sku:service-assembly-025",
        "category_name": "Services",
        "price": 180000,
        "condition": "BUENO",
        "stock": 0,
        "description": "Servicio de armado y configuración de PC gamer listo para usar.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Servicio limpieza y mantenimiento PC",
        "author": "TechFlow",
        "publisher": "TechFlow Servicios",
        "isbn": "sku:service-cleaning-026",
        "category_name": "Services",
        "price": 120000,
        "condition": "BUENO",
        "stock": 0,
        "description": "Mantenimiento preventivo y limpieza interna de PCs de gaming y trabajo.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    },
]


def seed_categories(db: Session):
    for name in _DEFAULT_CATEGORIES:
        if not db.query(CategoryModel).filter(CategoryModel.name == name).first():
            db.add(CategoryModel(name=name))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def seed_products(db: Session):
    if db.query(BookModel).count() > 0:
        return
    for data in _DEFAULT_BOOKS:
        cat = db.query(CategoryModel).filter(CategoryModel.name == data["category_name"]).first()
        db.add(BookModel(
            title=data["title"],
            author=data["author"],
            publisher=data["publisher"],
            isbn=data["isbn"],
            category_id=cat.id if cat else None,
            description=data["description"],
            cover_url=data["cover_url"],
            price=data.get("price"),
            condition=data.get("condition"),
            stock=data.get("stock"),
            published_flag=True,
            enriched_flag=False,
        ))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


seed_books = seed_products


def create_book(db: Session, book: Book) -> Book:
    m = BookModel(
        title=book.title,
        subtitle=book.subtitle,
        author=book.author,
        publisher=book.publisher,
        publication_year=book.publication_year,
        volume=book.volume,
        isbn=book.isbn,
        issn=book.issn,
        category_id=book.category_id,
        description=book.description,
        cover_url=book.cover_url,
        price=book.price,
        condition=book.condition,
        stock=book.stock,
        enriched_flag=book.enriched_flag,
        published_flag=book.published_flag,
    )

    db.add(m)
    try:
        db.commit()
        db.refresh(m)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Ya existe un libro con el ISBN {book.isbn}")
    except Exception:
        db.rollback()
        raise
    return _book(m)


def get_book(db: Session, book_id: int) -> Optional[Book]:
    m = db.query(BookModel).filter(BookModel.id == book_id).first()
    return _book(m) if m else None


def get_all_books(db: Session, skip: int, limit: int, published_only: bool) -> List[Book]:
    q = db.query(BookModel)
    if published_only:
        q = q.filter(BookModel.published_flag == True)
    return [_book(m) for m in q.offset(skip).limit(limit).all()]


def search_books(db: Session, query: str, skip: int, limit: int) -> List[Book]:
    return [_book(m) for m in db.query(BookModel).filter(
        or_(BookModel.title.ilike(f"%{query}%"),
            BookModel.author.ilike(f"%{query}%"),
            BookModel.isbn.ilike(f"%{query}%"))
    ).offset(skip).limit(limit).all()]


def update_book(db: Session, book_id: int, **kwargs) -> Optional[Book]:
    m = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not m:
        return None
    for k, v in kwargs.items():
        if hasattr(m, k):
            setattr(m, k, v)
    try:
        db.commit()
        db.refresh(m)
    except Exception:
        db.rollback()
        raise
    return _book(m)


def delete_book(db: Session, book_id: int) -> bool:
    m = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not m:
        return False
    db.delete(m)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


def get_all_categories(db: Session) -> List[Category]:
    return [_cat(m) for m in db.query(CategoryModel).all()]


def create_category(db: Session, name: str, description: str = None) -> Category:
    m = CategoryModel(name=name, description=description)
    db.add(m)
    try:
        db.commit()
        db.refresh(m)
    except Exception:
        db.rollback()
        raise
    return _cat(m)
