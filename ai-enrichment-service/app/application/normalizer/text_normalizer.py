import re
import unicodedata

# Suffixes stripped (longest first) when canonicalizing publisher names
_PUBLISHER_SUFFIXES: tuple[str, ...] = (
    " publishers",
    " publisher",
    " publishing",
    " editions",
    " edition",
    " editorial",
    " books",
    " book",
    " press",
    " group",
    " ltd.",
    " ltd",
    " inc.",
    " inc",
    " llc",
)

# Known variant → canonical form (applied after suffix stripping)
_PUBLISHER_ALIASES: dict[str, str] = {
    "harpercollins": "HarperCollins",
    "harper collins": "HarperCollins",
    "penguin random house": "Penguin Random House",
    "penguin": "Penguin",
    "random house": "Random House",
    "simon schuster": "Simon & Schuster",
    "simon and schuster": "Simon & Schuster",
    "hachette livre": "Hachette",
    "hachette book": "Hachette",
    "macmillan": "Macmillan",
    "scholastic": "Scholastic",
    "oxford university": "Oxford University Press",
    "cambridge university": "Cambridge University Press",
    "mit": "MIT Press",
    "university of chicago": "University of Chicago Press",
}


def remove_control_characters(text: str) -> str:
    return "".join(
        ch for ch in text if not unicodedata.category(ch).startswith("C")
    )


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_title(title: str | None) -> str | None:
    if not title:
        return None

    text = remove_control_characters(title)
    text = normalize_whitespace(text)
    text = remove_accents(text)

    return text.title() if text else None


def normalize_publisher(publisher: str | None) -> str | None:
    if not publisher:
        return None

    text = normalize_whitespace(publisher)
    text = remove_accents(text)
    if not text:
        return None

    # Check full name in alias map first (e.g. "Harper Collins")
    canonical = _PUBLISHER_ALIASES.get(text.lower())
    if canonical:
        return canonical

    # Strip trailing punctuation so "Inc." → "Inc" before suffix matching
    clean = re.sub(r"[.\s]+$", "", text).strip()
    lower = clean.lower()

    # Strip trailing generic suffixes to get the root name
    stripped = ""
    for suffix in _PUBLISHER_SUFFIXES:
        if lower.endswith(suffix):
            stripped = clean[: -len(suffix)].strip()
            break
    if stripped:
        canonical = _PUBLISHER_ALIASES.get(stripped.lower())
        if canonical:
            return canonical

    # Unknown publisher — return as-is (do not silently drop meaningful words)
    return text
