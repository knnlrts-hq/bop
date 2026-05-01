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
    existing = {f.name for f in assets_dir.iterdir()} if assets_dir.exists() else set()
    text = src.read_text(encoding="utf-8")
    text = strip_comments(text)
    text = convert_highlights(text)
    text = convert_images(text, existing)
    slug = slugify_filename(src.name)
    out_path = out_dir / slug
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for src in sorted(CHAPTERS_DIR.glob("*.md")):
        out = convert_file(src, OUT_DIR, ASSETS_DIR)
        print(f"  {src.name} -> {out.name}")


if __name__ == "__main__":
    main()
