import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from convert_obsidian import (
    slugify_filename,
    slugify_title,
    strip_comments,
    convert_highlights,
    convert_images,
    convert_callouts,
    split_into_sections,
    convert_file,
)


# --- slugify_filename ---

def test_slugify_sets():
    assert slugify_filename("01✓. Sets.md") == "01-sets.md"


def test_slugify_logic():
    assert slugify_filename("02✓. Logic.md") == "02-logic.md"


def test_slugify_counting():
    assert slugify_filename("03✓. Counting.md") == "03-counting.md"


# --- slugify_title ---

def test_slugify_title_basic():
    assert slugify_title("Introduction to Sets") == "introduction-to-sets"


def test_slugify_title_with_numbers():
    assert slugify_title("The Cartesian Product") == "the-cartesian-product"


def test_slugify_title_special_chars():
    assert slugify_title("Russell's Paradox") == "russell-s-paradox"


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
    assert convert_highlights("$x = 1$") == "$x = 1$"


# --- convert_callouts ---

def test_callout_success_collapsed():
    result = convert_callouts("> [!success]- Answer\n> $x = 1$\n")
    assert result == ":::{dropdown} Answer\n$x = 1$\n:::\n"


def test_callout_info_collapsed():
    result = convert_callouts("> [!info]- Mean Value Theorem\n> content\n")
    assert result == ":::{dropdown} Mean Value Theorem\ncontent\n:::\n"


def test_callout_multiline_body():
    inp = "> [!success]- Answer\n> line 1\n> line 2\n> line 3\n"
    result = convert_callouts(inp)
    assert result == ":::{dropdown} Answer\nline 1\nline 2\nline 3\n:::\n"


def test_callout_title_trailing_space_stripped():
    result = convert_callouts("> [!info]- Mean Value Theorem \n> body\n")
    assert "Mean Value Theorem\n" in result
    assert "Mean Value Theorem \n" not in result


def test_callout_no_callouts():
    text = "> regular blockquote\n> no callout here\n"
    assert convert_callouts(text) == text


def test_callout_preserves_surrounding_text():
    inp = "before\n> [!success]- Answer\n> body\nafter\n"
    result = convert_callouts(inp)
    assert result.startswith("before\n")
    assert result.endswith("after\n")
    assert ":::{dropdown} Answer" in result


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


# --- split_into_sections ---

def test_split_basic():
    text = "# 1.1 Introduction to Sets\ncontent 1\n# 1.2 Cartesian Product\ncontent 2\n"
    sections = split_into_sections(text)
    assert len(sections) == 2
    assert sections[0][0] == "01-1-introduction-to-sets"
    assert sections[1][0] == "01-2-cartesian-product"


def test_split_preamble_included_in_first_section():
    text = "Preamble text.\n# 1.1 Sets\ncontent\n"
    sections = split_into_sections(text)
    assert len(sections) == 1
    assert sections[0][1].startswith("Preamble text.")
    assert "# 1.1 Sets" in sections[0][1]


def test_split_no_sections_returns_empty():
    assert split_into_sections("just some text\n") == []


def test_split_slug_format():
    text = "# 2.10 Negating Statements\ncontent\n"
    sections = split_into_sections(text)
    assert sections[0][0] == "02-10-negating-statements"


def test_split_content_boundaries():
    text = "# 1.1 A\ncontent a\n# 1.2 B\ncontent b\n# 1.3 C\ncontent c\n"
    sections = split_into_sections(text)
    assert "content a" in sections[0][1]
    assert "content b" not in sections[0][1]
    assert "content b" in sections[1][1]
    assert "content c" in sections[2][1]


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
    assert "$x = 1$" in content


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


def test_convert_file_converts_callouts(tmp_path):
    out_dir = tmp_path / "docs" / "chapters"
    out_dir.mkdir(parents=True)
    assets_dir = tmp_path / "docs" / "assets"
    assets_dir.mkdir(parents=True)

    src = tmp_path / "01✓. Sets.md"
    src.write_text("> [!success]- Answer\n> $x = 1$\n", encoding="utf-8")

    out = convert_file(src, out_dir, assets_dir)

    content = out.read_text(encoding="utf-8")
    assert ":::{dropdown} Answer" in content
    assert "[!success]" not in content
