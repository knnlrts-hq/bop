# Design: GitHub Pages Hosting for Book of Proof Annotations

**Date:** 2026-05-01  
**Repo:** knnlrts-hq/bop  
**Branch:** claude/host-markdown-chapters-Egk2J

## Problem

The repo contains annotated chapters of *Book of Proof* by Richard Hammack, written in Obsidian-flavoured Markdown. They are not publicly readable in a rendered form. The goal is to host them on GitHub Pages using the same Sphinx + Furo + MyST stack as [simonw/nicar-2026-coding-agents](https://github.com/simonw/nicar-2026-coding-agents).

## Constraints

- Obsidian source files in `chapters/` must remain untouched (authors keep editing in Obsidian)
- Images will be added to the repo later; missing images must not crash the build
- TOC registration is manual (a human edits `docs/index.md` when a new chapter is ready)
- Stack must mirror the reference repo: Sphinx, Furo theme, MyST Parser, GitHub Actions

## Repository Structure

```
bop/
├── chapters/                        # Obsidian source — never modified by tooling
│   ├── 01✓. Sets.md
│   ├── 02✓. Logic.md
│   └── 03✓. Counting.md
├── docs/                            # Sphinx source root
│   ├── conf.py
│   ├── index.md                     # Pre-filled: intro + TOC for chapters 1-3
│   ├── requirements.txt
│   ├── assets/                      # Images land here (added manually later)
│   └── chapters/                    # GENERATED — git-ignored, rebuilt every run
│       ├── 01-sets.md
│       ├── 02-logic.md
│       └── 03-counting.md
├── scripts/
│   └── convert_obsidian.py          # Obsidian → MyST converter
├── tests/
│   └── test_convert_obsidian.py
└── .github/
    └── workflows/
        └── deploy.yml
```

`docs/chapters/` and `docs/_build/` are git-ignored.

## Conversion Script (`scripts/convert_obsidian.py`)

Reads every `.md` from `chapters/`, applies five transformations, writes output to `docs/chapters/` with a slugified filename. Creates `docs/assets/` if absent.

### Transformations (applied in order)

| # | Input (Obsidian) | Output (MyST) |
|---|---|---|
| 1 | Filename `01✓. Sets.md` | `01-sets.md` (strip non-alphanumeric, lowercase, collapse hyphens) |
| 2 | `%%IMPORTANT_FORMULA%%` | deleted (Obsidian comment syntax) |
| 3 | `==text==` | `<mark>text</mark>` |
| 4 | `![[fig.png\|500]]` (image exists) | `<img src="../assets/fig.png" width="500">` |
| 4 | `![[fig.png\|500]]` (image missing) | `<!-- TODO: missing image: fig.png -->` |
| 5 | Write to `docs/chapters/<slug>.md` | — |

Each transformation is a pure function (string in, string out) for testability.

### Invocation

```bash
python scripts/convert_obsidian.py
```

No arguments. Always reads from `chapters/`, always writes to `docs/chapters/`.

## Sphinx Configuration (`docs/conf.py`)

```python
project = "Book of Proof — Annotated"
author = "Richard Hammack (annotations by knnlrts-hq)"
extensions = ["myst_parser", "sphinx_copybutton"]
myst_enable_extensions = ["colon_fence", "html_image"]
html_theme = "furo"
master_doc = "index"
```

`html_image` is required for `{width=500px}` image attributes to render.  
MathJax is activated automatically by Furo when MyST encounters `$...$` or `$$...$$`.

## Dependencies (`docs/requirements.txt`)

```
sphinx==9.1.0
furo==2025.12.19
sphinx-copybutton==0.5.2
myst-parser==5.0.0
```

Pinned to match the reference repo.

## Index Page (`docs/index.md`)

Pre-filled on day one with:
- A brief description of *Book of Proof* (author, open-source status, that this is an annotated/solved edition)
- A MyST `{toctree}` directive listing all three current chapters
- Manual update required when a new chapter is added

## GitHub Actions (`/.github/workflows/deploy.yml`)

Triggers on push to `main`. Steps:

1. `actions/checkout@v4`
2. `actions/setup-python@v5` (Python 3.12)
3. `pip install -r docs/requirements.txt`
4. `python scripts/convert_obsidian.py`
5. `sphinx-build -b html docs docs/_build/html`
6. `peaceiris/actions-gh-pages@v4` — publishes `docs/_build/html` to `gh-pages` branch

**One-time manual step:** In GitHub repo Settings → Pages, set source to the `gh-pages` branch.

## Testing (`tests/test_convert_obsidian.py`)

Pure-function unit tests for each transformation:

```python
# Comments
assert strip_comments("before %%IMPORTANT_FORMULA%% after") == "before  after"
assert strip_comments("%%multi\nline%%") == ""

# Highlights
assert convert_highlights("==key idea==") == "<mark>key idea</mark>"
assert convert_highlights("no highlights here") == "no highlights here"

# Images — present
assert convert_images("![[fig.png|500]]", existing={"fig.png"}) == \
    '<img src="../assets/fig.png" width="500">'

# Images — missing
assert convert_images("![[missing.png|300]]", existing=set()) == \
    "<!-- TODO: missing image: missing.png -->"

# Slugify
assert slugify_filename("01✓. Sets.md") == "01-sets.md"
assert slugify_filename("02✓. Logic.md") == "02-logic.md"
```

Plus one filesystem integration test: creates a temp `chapters/` dir, runs the full script, asserts output file exists in `docs/chapters/` with correct name and transformed content.

Run with: `pytest tests/`

## Out of Scope

- Auto-discovery of new chapters (manual TOC registration is intentional)
- Custom CSS beyond Furo defaults
- Search index customisation
- Handling of Obsidian callouts (`> [!note]`) — not present in current files
