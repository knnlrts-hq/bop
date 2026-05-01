import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from convert_obsidian import (
    slugify_filename,
    strip_comments,
    convert_highlights,
    convert_images,
    convert_file,
)


# --- slugify_filename ---

def test_slugify_sets():
    assert slugify_filename("01✓. Sets.md") == "01-sets.md"


def test_slugify_logic():
    assert slugify_filename("02✓. Logic.md") == "02-logic.md"


def test_slugify_counting():
    assert slugify_filename("03✓. Counting.md") == "03-counting.md"


# --- strip_comments ---

def test_strip_inline_comment():
    assert strip_comments("before %%IMPORTANT_FORMULA%% after") == "before  after"


def test_strip_multiline_comment():
    assert strip_comments("a\n%%multi\nline%%\nb") == "a\n\nb"


def test_strip_no_comments():
    assert strip_comments("no comments here") == "no comments here"


def test_strip_empty_comment():
    assert strip_comments("%%%%") == ""


# --- convert_highlights ---

def test_highlight_basic():
    assert convert_highlights("==key idea==") == "<mark>key idea</mark>"


def test_highlight_inline():
    assert convert_highlights("text ==important== end") == "text <mark>important</mark> end"


def test_highlight_multiple():
    assert convert_highlights("==a== and ==b==") == "<mark>a</mark> and <mark>b</mark>"


def test_highlight_none():
    assert convert_highlights("no highlights here") == "no highlights here"


def test_highlight_preserves_math():
    # Dollar signs must not be touched
    assert convert_highlights("$x = 1$") == "$x = 1$"


# --- convert_images ---

def test_image_with_width_present():
    result = convert_images("![[fig.png|500]]", {"fig.png"})
    assert result == '<img src="../assets/fig.png" width="500">'


def test_image_no_width_present():
    result = convert_images("![[fig.png]]", {"fig.png"})
    assert result == '<img src="../assets/fig.png">'


def test_image_missing_with_width():
    result = convert_images("![[missing.png|300]]", set())
    assert result == "<!-- TODO: missing image: missing.png -->"


def test_image_missing_no_width():
    result = convert_images("![[missing.png]]", set())
    assert result == "<!-- TODO: missing image: missing.png -->"


def test_image_none():
    assert convert_images("no images here", set()) == "no images here"


def test_image_preserves_surrounding_text():
    result = convert_images("before ![[fig.png|100]] after", {"fig.png"})
    assert result == 'before <img src="../assets/fig.png" width="100"> after'


# --- convert_file (integration) ---

def test_convert_file(tmp_path):
    chapters_dir = tmp_path / "chapters"
    chapters_dir.mkdir()
    out_dir = tmp_path / "docs" / "chapters"
    out_dir.mkdir(parents=True)
    assets_dir = tmp_path / "docs" / "assets"
    assets_dir.mkdir(parents=True)

    src = chapters_dir / "01✓. Sets.md"
    src.write_text(
        "%%comment%%\n==highlight== and ![[fig.png|300]]\n$x = 1$\n",
        encoding="utf-8",
    )
    (assets_dir / "fig.png").write_bytes(b"")

    out = convert_file(src, out_dir, assets_dir)

    assert out.name == "01-sets.md"
    content = out.read_text(encoding="utf-8")
    assert "%%comment%%" not in content
    assert "<mark>highlight</mark>" in content
    assert '<img src="../assets/fig.png" width="300">' in content
    assert "$x = 1$" in content  # math untouched


def test_convert_file_missing_image(tmp_path):
    out_dir = tmp_path / "docs" / "chapters"
    out_dir.mkdir(parents=True)
    assets_dir = tmp_path / "docs" / "assets"
    assets_dir.mkdir(parents=True)

    src = tmp_path / "02✓. Logic.md"
    src.write_text("![[ghost.png|200]]\n", encoding="utf-8")

    out = convert_file(src, out_dir, assets_dir)

    content = out.read_text(encoding="utf-8")
    assert "<!-- TODO: missing image: ghost.png -->" in content
