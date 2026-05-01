import re
import unicodedata
from pathlib import Path

CHAPTERS_DIR = Path("chapters")
OUT_DIR = Path("docs/chapters")
ASSETS_DIR = Path("docs/assets")


def slugify_filename(name: str) -> str:
    stem = Path(name).stem
    normalized = unicodedata.normalize("NFKD", stem)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slugged = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower())
    return slugged.strip("-") + ".md"


def strip_comments(text: str) -> str:
    return re.sub(r"%%.*?%%", "", text, flags=re.DOTALL)


def convert_highlights(text: str) -> str:
    return re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)


def convert_images(text: str, existing: set) -> str:
    def replace(match):
        filename = match.group(1)
        width = match.group(2)
        if filename in existing:
            if width:
                return f'<img src="../assets/{filename}" width="{width}">'
            return f'<img src="../assets/{filename}">'
        return f"<!-- TODO: missing image: {filename} -->"

    return re.sub(r"!\[\[([^\]|]+?)(?:\|(\d+))?\]\]", replace, text)


def convert_file(src: Path, out_dir: Path, assets_dir: Path) -> Path:
    raise NotImplementedError


def main():
    raise NotImplementedError


if __name__ == "__main__":
    main()
