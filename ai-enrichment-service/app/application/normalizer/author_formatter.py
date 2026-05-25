import re
from app.application.normalizer.text_normalizer import (
    normalize_whitespace,
    remove_accents
)


def format_author(author: str | None) -> str | None:
    if not author:
        return None

    # Separar múltiples autores por ;
    authors = re.split(r"\s*;\s*", author.strip())

    formatted = [_format_single(a) for a in authors if a.strip()]

    return "; ".join(formatted) if formatted else None


def _format_single(name: str) -> str:
    name = normalize_whitespace(name)
    name = remove_accents(name)

    # Si ya está en formato "Apellido, Nombre"
    if "," in name:
        return name.title()

    parts = name.split()

    if len(parts) == 1:
        return parts[0].title()

    if len(parts) == 2:
        return f"{parts[1].title()}, {parts[0].title()}"

    # Más de dos nombres
    surname = parts[-1].title()
    given = " ".join(p.title() for p in parts[:-1])

    return f"{surname}, {given}"
