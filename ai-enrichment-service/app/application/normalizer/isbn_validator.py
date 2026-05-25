def clean_isbn(isbn: str) -> str:
    return isbn.replace("-", "").replace(" ", "").strip()


def validate_and_normalize(isbn: str) -> str | None:
    if not isbn:
        return None

    cleaned = clean_isbn(isbn)

    if len(cleaned) == 10:
        if not validate_isbn10(cleaned):
            return None
        return isbn10_to_isbn13(cleaned)

    if len(cleaned) == 13:
        return cleaned if validate_isbn13(cleaned) else None

    return None


# 🔥 VALIDACIÓN REAL ISBN-10
def validate_isbn10(isbn10: str) -> bool:
    if len(isbn10) != 10:
        return False

    total = 0

    for i, char in enumerate(isbn10):
        if char == "X" and i == 9:
            digit = 10
        elif char.isdigit():
            digit = int(char)
        else:
            return False

        total += digit * (10 - i)

    return total % 11 == 0


# 🔥 CONVERSIÓN
def isbn10_to_isbn13(isbn10: str) -> str:
    core = "978" + isbn10[:-1]
    check = compute_isbn13_check(core)
    return core + str(check)


# 🔥 VALIDACIÓN ISBN-13
def validate_isbn13(isbn13: str) -> bool:
    if len(isbn13) != 13 or not isbn13.isdigit():
        return False

    total = sum(
        int(d) * (1 if i % 2 == 0 else 3)
        for i, d in enumerate(isbn13)
    )

    return total % 10 == 0


def compute_isbn13_check(isbn12: str) -> int:
    total = sum(
        int(d) * (1 if i % 2 == 0 else 3)
        for i, d in enumerate(isbn12)
    )

    remainder = total % 10
    return 0 if remainder == 0 else 10 - remainder