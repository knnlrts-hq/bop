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
