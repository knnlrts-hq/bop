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
    raise NotImplementedError


def convert_highlights(text: str) -> str:
    raise NotImplementedError


def convert_images(text: str, existing: set) -> str:
    raise NotImplementedError


def convert_file(src: Path, out_dir: Path, assets_dir: Path) -> Path:
    raise NotImplementedError


def main():
    raise NotImplementedError


if __name__ == "__main__":
    main()
