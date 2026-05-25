"""Seed pricing decisions and references into pricing_db (matches the technology catalog items)."""
import datetime
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pricing-service"))

from app.infrastructure.database import (  # noqa: E402
    Base,
    BookConditionDB,
    PricingDecisionModel,
    PricingReferenceModel,
)

DATABASE_URL = os.getenv(
    "PRICING_DATABASE_URL",
    "postgresql://bookflow:bookflow123@localhost:5432/pricing_db",
)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

_CONDITION_FACTORS = {
    BookConditionDB.NUEVO: 1.0,
    BookConditionDB.BUENO: 0.75,
    BookConditionDB.ACEPTABLE: 0.50,
    BookConditionDB.DETERIORADO: 0.25,
}

DECISIONS = [
    {"book_id": "sku:rog-strix-pc-001", "book_title": "ASUS ROG Strix Gaming PC", "condition": BookConditionDB.NUEVO, "base_price": 680.00, "references": [{"source": "mercado_computo", "price": 660.00}, {"source": "mercado_computo", "price": 690.00}]},
    {"book_id": "sku:msi-aegis-ti5-002", "book_title": "MSI Aegis Ti5 Gaming PC", "condition": BookConditionDB.BUENO, "base_price": 720.00, "references": [{"source": "mercado_tecnologia", "price": 700.00}, {"source": "mercado_tecnologia", "price": 735.00}]},
    {"book_id": "sku:flow-x16-003", "book_title": "ASUS ROG Flow X16", "condition": BookConditionDB.NUEVO, "base_price": 520.00, "references": [{"source": "mercado_tecnologia", "price": 510.00}, {"source": "mercado_tecnologia", "price": 535.00}]},
    {"book_id": "sku:alienware-x16-004", "book_title": "Dell Alienware x16", "condition": BookConditionDB.BUENO, "base_price": 599.00, "references": [{"source": "mercado_computo", "price": 585.00}, {"source": "mercado_computo", "price": 610.00}]},
    {"book_id": "sku:rtx-4080-005", "book_title": "NVIDIA GeForce RTX 4080", "condition": BookConditionDB.NUEVO, "base_price": 740.00, "references": [{"source": "tienda_gpu", "price": 720.00}, {"source": "tienda_gpu", "price": 760.00}]},
    {"book_id": "sku:rx-7900-006", "book_title": "AMD Radeon RX 7900 XT", "condition": BookConditionDB.BUENO, "base_price": 650.00, "references": [{"source": "tienda_gpu", "price": 630.00}, {"source": "tienda_gpu", "price": 670.00}]},
    {"book_id": "sku:i9-14900k-007", "book_title": "Intel Core i9-14900K", "condition": BookConditionDB.NUEVO, "base_price": 145.00, "references": [{"source": "tienda_cpu", "price": 142.00}, {"source": "tienda_cpu", "price": 148.00}]},
    {"book_id": "sku:ryzen-7950x-008", "book_title": "AMD Ryzen 9 7950X", "condition": BookConditionDB.NUEVO, "base_price": 139.00, "references": [{"source": "tienda_cpu", "price": 136.00}, {"source": "tienda_cpu", "price": 141.00}]},
    {"book_id": "sku:strix-z790-009", "book_title": "ASUS ROG Strix Z790-E", "condition": BookConditionDB.BUENO, "base_price": 139.00, "references": [{"source": "tienda_mobo", "price": 136.00}, {"source": "tienda_mobo", "price": 143.00}]},
    {"book_id": "sku:b650-carbon-010", "book_title": "MSI MPG B650 Carbon", "condition": BookConditionDB.BUENO, "base_price": 124.00, "references": [{"source": "tienda_mobo", "price": 120.00}, {"source": "tienda_mobo", "price": 129.00}]},
    {"book_id": "sku:ddr5-32gb-011", "book_title": "Corsair Vengeance DDR5 32GB", "condition": BookConditionDB.NUEVO, "base_price": 82.00, "references": [{"source": "tienda_ram", "price": 80.00}, {"source": "tienda_ram", "price": 85.00}]},
    {"book_id": "sku:trident-z5-012", "book_title": "G.Skill Trident Z5 RGB 32GB", "condition": BookConditionDB.BUENO, "base_price": 84.00, "references": [{"source": "tienda_ram", "price": 82.00}, {"source": "tienda_ram", "price": 87.00}]},
    {"book_id": "sku:990-pro-2tb-013", "book_title": "Samsung 990 Pro 2TB", "condition": BookConditionDB.NUEVO, "base_price": 76.00, "references": [{"source": "tienda_storage", "price": 73.00}, {"source": "tienda_storage", "price": 79.00}]},
    {"book_id": "sku:sn850x-2tb-014", "book_title": "WD Black SN850X 2TB", "condition": BookConditionDB.BUENO, "base_price": 72.00, "references": [{"source": "tienda_storage", "price": 69.00}, {"source": "tienda_storage", "price": 75.00}]},
    {"book_id": "sku:h150i-015", "book_title": "Corsair iCUE H150i Elite", "condition": BookConditionDB.BUENO, "base_price": 78.00, "references": [{"source": "tienda_cooling", "price": 75.00}, {"source": "tienda_cooling", "price": 82.00}]},
    {"book_id": "sku:nh-d15-016", "book_title": "Noctua NH-D15", "condition": BookConditionDB.BUENO, "base_price": 42.00, "references": [{"source": "tienda_cooling", "price": 40.00}, {"source": "tienda_cooling", "price": 44.00}]},
    {"book_id": "sku:odyssey-g7-017", "book_title": "Samsung Odyssey G7 27\"", "condition": BookConditionDB.BUENO, "base_price": 185.00, "references": [{"source": "tienda_monitors", "price": 180.00}, {"source": "tienda_monitors", "price": 190.00}]},
    {"book_id": "sku:ultragear-34-018", "book_title": "LG UltraGear 34\"", "condition": BookConditionDB.NUEVO, "base_price": 249.00, "references": [{"source": "tienda_monitors", "price": 240.00}, {"source": "tienda_monitors", "price": 255.00}]},
    {"book_id": "sku:blackwidow-v4-019", "book_title": "Razer BlackWidow V4 Pro", "condition": BookConditionDB.BUENO, "base_price": 79.00, "references": [{"source": "tienda_peripherals", "price": 76.00}, {"source": "tienda_peripherals", "price": 82.00}]},
    {"book_id": "sku:g502x-020", "book_title": "Logitech G502 X", "condition": BookConditionDB.NUEVO, "base_price": 32.00, "references": [{"source": "tienda_peripherals", "price": 30.00}, {"source": "tienda_peripherals", "price": 34.00}]},
    {"book_id": "sku:rm850x-021", "book_title": "Corsair RM850x 850W", "condition": BookConditionDB.NUEVO, "base_price": 65.00, "references": [{"source": "tienda_psu", "price": 62.00}, {"source": "tienda_psu", "price": 68.00}]},
    {"book_id": "sku:focus-gx-022", "book_title": "Seasonic Focus GX-750", "condition": BookConditionDB.BUENO, "base_price": 59.00, "references": [{"source": "tienda_psu", "price": 56.00}, {"source": "tienda_psu", "price": 62.00}]},
    {"book_id": "sku:h510-023", "book_title": "NZXT H510", "condition": BookConditionDB.BUENO, "base_price": 32.00, "references": [{"source": "tienda_cases", "price": 30.00}, {"source": "tienda_cases", "price": 34.00}]},
    {"book_id": "sku:lancool-ii-024", "book_title": "Lian Li Lancool II", "condition": BookConditionDB.BUENO, "base_price": 42.00, "references": [{"source": "tienda_cases", "price": 40.00}, {"source": "tienda_cases", "price": 44.00}]},
    {"book_id": "sku:service-assembly-025", "book_title": "Servicio armado PC gaming", "condition": BookConditionDB.BUENO, "base_price": 18.00, "references": [{"source": "servicio_interno", "price": 17.50}, {"source": "servicio_interno", "price": 18.50}]},
    {"book_id": "sku:service-cleaning-026", "book_title": "Servicio limpieza y mantenimiento PC", "condition": BookConditionDB.BUENO, "base_price": 12.00, "references": [{"source": "servicio_interno", "price": 11.50}, {"source": "servicio_interno", "price": 12.50}]},
]


def _build_explanation(book_title: str, condition: BookConditionDB, refs: list[dict], base_price: float, suggested_price: float) -> str:
    ref_count = len(refs)
    source_names = list({r["source"] for r in refs})
    sources_str = ", ".join(source_names)
    factor = _CONDITION_FACTORS[condition]
    return (
        f"Precio calculado con base en {ref_count} referencia(s) de {sources_str} "
        f"(promedio base: ${base_price:.2f} USD). "
        f"Factor de condición {condition.value} aplicado ({factor:.2f}). "
        f"Precio sugerido final: ${suggested_price:.2f} USD."
    )


def run() -> None:
    session = Session()
    try:
        seeded = 0
        for d in DECISIONS:
            existing = session.query(PricingDecisionModel).filter_by(book_id=d["book_id"]).first()
            if existing:
                continue

            condition: BookConditionDB = d["condition"]
            factor = _CONDITION_FACTORS[condition]
            base_price: float = d["base_price"]
            suggested_price = round(base_price * factor, 2)
            refs: list[dict] = d["references"]
            source = refs[0]["source"] if refs else "internal_rules"

            explanation = _build_explanation(
                book_title=d["book_title"],
                condition=condition,
                refs=refs,
                base_price=base_price,
                suggested_price=suggested_price,
            )

            decision = PricingDecisionModel(
                book_id=d["book_id"],
                book_title=d["book_title"],
                condition=condition,
                base_price=base_price,
                condition_factor=factor,
                suggested_price=suggested_price,
                references_used=len(refs),
                source=source,
                explanation=explanation,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )
            session.add(decision)
            session.flush()

            for ref_data in refs:
                ref = PricingReferenceModel(
                    book_id=d["book_id"],
                    decision_id=decision.id,
                    source=ref_data["source"],
                    price=ref_data["price"],
                    currency="USD",
                    observed_at=datetime.datetime.now(datetime.timezone.utc),
                )
                session.add(ref)

            seeded += 1

        session.commit()
        print(f"Seeded {seeded} pricing decisions ({len(DECISIONS) - seeded} already existed).")
    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
