"""Seed inventory items into inventory_db (matches the technology catalog items)."""
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "inventory-service"))

from app.infrastructure.database import Base, InventoryItemModel, ItemConditionDB  # noqa: E402

DATABASE_URL = os.getenv(
    "INVENTORY_DATABASE_URL",
    "postgresql://bookflow:bookflow123@localhost:5432/inventory_db",
)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

_COND = {
    "NUEVO": ItemConditionDB.new,
    "BUENO": ItemConditionDB.good,
    "ACEPTABLE": ItemConditionDB.acceptable,
    "DETERIORADO": ItemConditionDB.poor,
}

ITEMS = [
    {"book_reference": "sku:rog-strix-pc-001", "title": "ASUS ROG Strix Gaming PC", "author": "ASUS", "isbn": "sku:rog-strix-pc-001", "quantity_available": 5, "condition": "NUEVO"},
    {"book_reference": "sku:msi-aegis-ti5-002", "title": "MSI Aegis Ti5 Gaming PC", "author": "MSI", "isbn": "sku:msi-aegis-ti5-002", "quantity_available": 3, "condition": "BUENO"},
    {"book_reference": "sku:flow-x16-003", "title": "ASUS ROG Flow X16", "author": "ASUS", "isbn": "sku:flow-x16-003", "quantity_available": 4, "condition": "NUEVO"},
    {"book_reference": "sku:alienware-x16-004", "title": "Dell Alienware x16", "author": "Dell", "isbn": "sku:alienware-x16-004", "quantity_available": 2, "condition": "BUENO"},
    {"book_reference": "sku:rtx-4080-005", "title": "NVIDIA GeForce RTX 4080", "author": "NVIDIA", "isbn": "sku:rtx-4080-005", "quantity_available": 7, "condition": "NUEVO"},
    {"book_reference": "sku:rx-7900-006", "title": "AMD Radeon RX 7900 XT", "author": "AMD", "isbn": "sku:rx-7900-006", "quantity_available": 5, "condition": "BUENO"},
    {"book_reference": "sku:i9-14900k-007", "title": "Intel Core i9-14900K", "author": "Intel", "isbn": "sku:i9-14900k-007", "quantity_available": 8, "condition": "NUEVO"},
    {"book_reference": "sku:ryzen-7950x-008", "title": "AMD Ryzen 9 7950X", "author": "AMD", "isbn": "sku:ryzen-7950x-008", "quantity_available": 6, "condition": "NUEVO"},
    {"book_reference": "sku:strix-z790-009", "title": "ASUS ROG Strix Z790-E", "author": "ASUS", "isbn": "sku:strix-z790-009", "quantity_available": 10, "condition": "BUENO"},
    {"book_reference": "sku:b650-carbon-010", "title": "MSI MPG B650 Carbon", "author": "MSI", "isbn": "sku:b650-carbon-010", "quantity_available": 7, "condition": "BUENO"},
    {"book_reference": "sku:ddr5-32gb-011", "title": "Corsair Vengeance DDR5 32GB", "author": "Corsair", "isbn": "sku:ddr5-32gb-011", "quantity_available": 14, "condition": "NUEVO"},
    {"book_reference": "sku:trident-z5-012", "title": "G.Skill Trident Z5 RGB 32GB", "author": "G.Skill", "isbn": "sku:trident-z5-012", "quantity_available": 12, "condition": "BUENO"},
    {"book_reference": "sku:990-pro-2tb-013", "title": "Samsung 990 Pro 2TB", "author": "Samsung", "isbn": "sku:990-pro-2tb-013", "quantity_available": 11, "condition": "NUEVO"},
    {"book_reference": "sku:sn850x-2tb-014", "title": "WD Black SN850X 2TB", "author": "Western Digital", "isbn": "sku:sn850x-2tb-014", "quantity_available": 9, "condition": "BUENO"},
    {"book_reference": "sku:h150i-015", "title": "Corsair iCUE H150i Elite", "author": "Corsair", "isbn": "sku:h150i-015", "quantity_available": 8, "condition": "BUENO"},
    {"book_reference": "sku:nh-d15-016", "title": "Noctua NH-D15", "author": "Noctua", "isbn": "sku:nh-d15-016", "quantity_available": 13, "condition": "BUENO"},
    {"book_reference": "sku:odyssey-g7-017", "title": "Samsung Odyssey G7 27\"", "author": "Samsung", "isbn": "sku:odyssey-g7-017", "quantity_available": 10, "condition": "BUENO"},
    {"book_reference": "sku:ultragear-34-018", "title": "LG UltraGear 34\"", "author": "LG", "isbn": "sku:ultragear-34-018", "quantity_available": 6, "condition": "NUEVO"},
    {"book_reference": "sku:blackwidow-v4-019", "title": "Razer BlackWidow V4 Pro", "author": "Razer", "isbn": "sku:blackwidow-v4-019", "quantity_available": 9, "condition": "BUENO"},
    {"book_reference": "sku:g502x-020", "title": "Logitech G502 X", "author": "Logitech", "isbn": "sku:g502x-020", "quantity_available": 15, "condition": "NUEVO"},
    {"book_reference": "sku:rm850x-021", "title": "Corsair RM850x 850W", "author": "Corsair", "isbn": "sku:rm850x-021", "quantity_available": 12, "condition": "NUEVO"},
    {"book_reference": "sku:focus-gx-022", "title": "Seasonic Focus GX-750", "author": "Seasonic", "isbn": "sku:focus-gx-022", "quantity_available": 10, "condition": "BUENO"},
    {"book_reference": "sku:h510-023", "title": "NZXT H510", "author": "NZXT", "isbn": "sku:h510-023", "quantity_available": 11, "condition": "BUENO"},
    {"book_reference": "sku:lancool-ii-024", "title": "Lian Li Lancool II", "author": "Lian Li", "isbn": "sku:lancool-ii-024", "quantity_available": 9, "condition": "BUENO"},
    {"book_reference": "sku:service-assembly-025", "title": "Servicio armado PC gaming", "author": "TechSupport", "isbn": "sku:service-assembly-025", "quantity_available": 30, "condition": "BUENO"},
    {"book_reference": "sku:service-cleaning-026", "title": "Servicio limpieza y mantenimiento PC", "author": "TechSupport", "isbn": "sku:service-cleaning-026", "quantity_available": 25, "condition": "BUENO"},
]


def run() -> None:
    session = Session()
    try:
        for item_data in ITEMS:
            condition_str = item_data.pop("condition")
            existing = session.query(InventoryItemModel).filter_by(
                book_reference=item_data["book_reference"]
            ).first()
            if not existing:
                item = InventoryItemModel(
                    **item_data,
                    condition=_COND[condition_str],
                )
                session.add(item)

        session.commit()
        print(f"Seeded {len(ITEMS)} inventory items.")
    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
