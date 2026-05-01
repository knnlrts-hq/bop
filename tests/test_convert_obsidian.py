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
