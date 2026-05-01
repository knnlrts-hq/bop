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
