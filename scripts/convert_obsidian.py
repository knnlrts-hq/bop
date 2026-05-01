import re
import unicodedata
from pathlib import Path

CHAPTERS_DIR = Path("chapters")
OUT_DIR = Path("docs/chapters")
ASSETS_DIR = Path("docs/assets")
INDEX_PATH = Path("docs/index.md")


def slugify_filename(name: str) -> str:
    stem = Path(name).stem
    normalized = unicodedata.normalize("NFKD", stem)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slugged = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower())
    return slugged.strip("-") + ".md"


def slugify_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")


def strip_comments(text: str) -> str:
    return re.sub(r"%%.*?%%", "", text, flags=re.DOTALL)


def convert_highlights(text: str) -> str:
    return re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)


def convert_callouts(text: str) -> str:
    def replace(match):
        title = match.group(1).strip()
        body = match.group(2)
        stripped = re.sub(r"^> ?", "", body, flags=re.MULTILINE)
        return f":::{{dropdown}} {title}\n{stripped}:::\n"

    return re.sub(
        r"> ?\[!\w+\][-+]? ?(.*)\n((?:> ?[^\n]*\n)*)",
        replace,
        text,
    )


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


def split_into_sections(text: str) -> list[tuple[str, str]]:
    """Split chapter text at # X.Y headers. Returns list of (slug, content)."""
    header_pattern = re.compile(r"^(# (\d+)\.(\d+) (.+))$", re.MULTILINE)
    matches = list(header_pattern.finditer(text))

    if not matches:
        return []

    sections = []
    for i, match in enumerate(matches):
        chapter_num = int(match.group(2))
        section_num = int(match.group(3))
        title = match.group(4).strip()

        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        # Include any preamble text before the first section header
        if i == 0 and start > 0:
            content = text[:end]
        else:
            content = text[start:end]

        slug = f"{chapter_num:02d}-{section_num}-{slugify_title(title)}"
        sections.append((slug, content))

    return sections


def update_index_toctree(slugs: list[str]) -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    entries = "\n".join(f"chapters/{s}" for s in slugs)
    new_toctree = (
        "```{toctree}\n"
        ":maxdepth: 2\n"
        ":caption: Sections\n"
        "\n"
        f"{entries}\n"
        "```"
    )
    text = re.sub(r"```\{toctree\}.*?```", new_toctree, text, flags=re.DOTALL)
    INDEX_PATH.write_text(text, encoding="utf-8")


def convert_file(src: Path, out_dir: Path, assets_dir: Path) -> Path:
    existing = {f.name for f in assets_dir.iterdir()} if assets_dir.exists() else set()
    text = src.read_text(encoding="utf-8")
    text = strip_comments(text)
    text = convert_highlights(text)
    text = convert_callouts(text)
    text = convert_images(text, existing)
    slug = slugify_filename(src.name)
    out_path = out_dir / slug
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    existing = {f.name for f in ASSETS_DIR.iterdir()} if ASSETS_DIR.exists() else set()

    all_slugs = []

    for src in sorted(CHAPTERS_DIR.glob("*.md")):
        text = src.read_text(encoding="utf-8")
        text = strip_comments(text)
        text = convert_highlights(text)
        text = convert_callouts(text)
        text = convert_images(text, existing)

        for slug, content in split_into_sections(text):
            out_path = OUT_DIR / f"{slug}.md"
            out_path.write_text(content, encoding="utf-8")
            all_slugs.append(slug)
            print(f"  {src.name} -> {out_path.name}")

    update_index_toctree(all_slugs)


if __name__ == "__main__":
    main()
