from slugify import slugify


def generate_slug(text: str, max_length: int = 150) -> str:
    return slugify(text, max_length=max_length)
