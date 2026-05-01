# GitHub Pages Hosting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the annotated *Book of Proof* chapters as a Sphinx-generated website hosted on GitHub Pages.

**Architecture:** A Python script converts Obsidian-flavoured Markdown in `chapters/` into MyST-compliant Markdown in `docs/chapters/` (generated, git-ignored). Sphinx then builds an HTML site from `docs/` using the Furo theme and MyST Parser. GitHub Actions runs this pipeline on every push to `main` and deploys the result to the `gh-pages` branch.

**Tech Stack:** Python 3.12, pytest, Sphinx 9.1.0, Furo, MyST Parser 5.0.0, sphinx-copybutton, GitHub Actions, peaceiris/actions-gh-pages.

---

## Background: What You Need to Know

### The Problem with Obsidian Markdown

Obsidian is a note-taking app that extends standard Markdown. Its flavour is **incompatible** with Sphinx/MyST in three ways this codebase uses:

| Obsidian syntax | Meaning | MyST equivalent |
|---|---|---|
| `%%comment%%` | Hidden comment block | Delete entirely |
| `==text==` | Highlighted text | `<mark>text</mark>` |
| `![[image.png\|500]]` | Embedded image with pixel width | `<img src="../assets/image.png" width="500">` |

LaTeX math (`$...$` and `$$...$$`) and raw HTML (`<table>`, `<span>`) are already valid in MyST — no conversion needed.

### What MyST and Sphinx are

**MyST Parser** is a Sphinx extension that lets you write documentation in Markdown instead of reStructuredText. **Sphinx** is a documentation generator that takes those files and produces HTML. **Furo** is a clean, responsive Sphinx theme.

### The source files

The three chapter files in `chapters/` have Unicode in their filenames (`01✓. Sets.md`). Sphinx can't handle Unicode in document paths, so the conversion script renames them to clean slugs (`01-sets.md`).

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `.gitignore` | Create | Exclude `docs/chapters/` and `docs/_build/` |
| `docs/assets/.gitkeep` | Create | Track the assets dir (images go here later) |
| `scripts/convert_obsidian.py` | Create | Obsidian → MyST converter (5 pure functions + main) |
| `tests/test_convert_obsidian.py` | Create | Unit tests for each function + one integration test |
| `docs/conf.py` | Create | Sphinx configuration |
| `docs/requirements.txt` | Create | Pinned Sphinx dependencies |
| `docs/index.md` | Create | Landing page with intro and TOC for chapters 1–3 |
| `.github/workflows/deploy.yml` | Create | CI/CD: convert → build → deploy |

---

## Task 1: Scaffolding

**Files:**
- Create: `.gitignore`
- Create: `docs/assets/.gitkeep`
- Create: `scripts/convert_obsidian.py` (skeleton only)
- Create: `tests/test_convert_obsidian.py` (skeleton only)

No tests in this task — it's pure setup.

- [ ] **Step 1: Create `.gitignore`**

```
# Sphinx build output
docs/_build/

# Generated MyST files (rebuilt by convert_obsidian.py on every build)
docs/chapters/
```

- [ ] **Step 2: Create `docs/assets/.gitkeep`**

Create an empty file at that path. This tells git to track the directory even though it's empty.

```bash
mkdir -p docs/assets
touch docs/assets/.gitkeep
```

- [ ] **Step 3: Create the skeleton `scripts/convert_obsidian.py`**

This skeleton makes the file importable by tests before any functions are implemented. Functions will be filled in task by task.

```python
import re
import unicodedata
from pathlib import Path

CHAPTERS_DIR = Path("chapters")
OUT_DIR = Path("docs/chapters")
ASSETS_DIR = Path("docs/assets")


def slugify_filename(name: str) -> str:
    raise NotImplementedError


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
```

- [ ] **Step 4: Create the skeleton `tests/test_convert_obsidian.py`**

```python
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
```

- [ ] **Step 5: Install pytest**

```bash
pip install pytest
```

- [ ] **Step 6: Verify the skeleton imports cleanly**

```bash
pytest tests/test_convert_obsidian.py -v
```

Expected output: `no tests ran` (0 collected). No import errors.

- [ ] **Step 7: Commit**

```bash
git add .gitignore docs/assets/.gitkeep scripts/convert_obsidian.py tests/test_convert_obsidian.py
git commit -m "chore: scaffold conversion script, test file, gitignore, assets dir"
```

---

## Task 2: `slugify_filename`

**Files:**
- Modify: `tests/test_convert_obsidian.py` (append tests)
- Modify: `scripts/convert_obsidian.py` (implement function)

`slugify_filename` converts the Obsidian filename to a URL-safe slug. Transformation chain: strip extension → NFKD-normalize → encode ASCII (drops ✓) → lowercase → replace non-alphanumeric runs with `-` → strip leading/trailing `-` → add `.md`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_convert_obsidian.py`:

```python


# --- slugify_filename ---

def test_slugify_sets():
    assert slugify_filename("01✓. Sets.md") == "01-sets.md"


def test_slugify_logic():
    assert slugify_filename("02✓. Logic.md") == "02-logic.md"


def test_slugify_counting():
    assert slugify_filename("03✓. Counting.md") == "03-counting.md"
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
pytest tests/test_convert_obsidian.py::test_slugify_sets -v
```

Expected: `FAILED` with `NotImplementedError`.

- [ ] **Step 3: Implement `slugify_filename`**

Replace the `raise NotImplementedError` in `scripts/convert_obsidian.py`:

```python
def slugify_filename(name: str) -> str:
    stem = Path(name).stem
    normalized = unicodedata.normalize("NFKD", stem)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slugged = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower())
    return slugged.strip("-") + ".md"
```

- [ ] **Step 4: Run to confirm tests pass**

```bash
pytest tests/test_convert_obsidian.py -k slugify -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/convert_obsidian.py tests/test_convert_obsidian.py
git commit -m "feat: implement slugify_filename"
```

---

## Task 3: `strip_comments`

**Files:**
- Modify: `tests/test_convert_obsidian.py` (append tests)
- Modify: `scripts/convert_obsidian.py` (implement function)

Obsidian comment syntax: `%%anything here%%`. The regex uses `re.DOTALL` so `%%` can span newlines.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_convert_obsidian.py`:

```python


# --- strip_comments ---

def test_strip_inline_comment():
    assert strip_comments("before %%IMPORTANT_FORMULA%% after") == "before  after"


def test_strip_multiline_comment():
    assert strip_comments("a\n%%multi\nline%%\nb") == "a\n\nb"


def test_strip_no_comments():
    assert strip_comments("no comments here") == "no comments here"


def test_strip_empty_comment():
    assert strip_comments("%%%%") == ""
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
pytest tests/test_convert_obsidian.py -k strip_comments -v
```

Expected: `4 failed` with `NotImplementedError`.

- [ ] **Step 3: Implement `strip_comments`**

```python
def strip_comments(text: str) -> str:
    return re.sub(r"%%.*?%%", "", text, flags=re.DOTALL)
```

- [ ] **Step 4: Run to confirm tests pass**

```bash
pytest tests/test_convert_obsidian.py -k strip_comments -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/convert_obsidian.py tests/test_convert_obsidian.py
git commit -m "feat: implement strip_comments"
```

---

## Task 4: `convert_highlights`

**Files:**
- Modify: `tests/test_convert_obsidian.py` (append tests)
- Modify: `scripts/convert_obsidian.py` (implement function)

Obsidian `==text==` becomes `<mark>text</mark>`. The `<mark>` HTML element renders as highlighted text in all modern browsers and passes through MyST's HTML rendering.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_convert_obsidian.py`:

```python


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
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
pytest tests/test_convert_obsidian.py -k highlight -v
```

Expected: `5 failed` with `NotImplementedError`.

- [ ] **Step 3: Implement `convert_highlights`**

```python
def convert_highlights(text: str) -> str:
    return re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)
```

- [ ] **Step 4: Run to confirm tests pass**

```bash
pytest tests/test_convert_obsidian.py -k highlight -v
```

Expected: `5 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/convert_obsidian.py tests/test_convert_obsidian.py
git commit -m "feat: implement convert_highlights"
```

---

## Task 5: `convert_images`

**Files:**
- Modify: `tests/test_convert_obsidian.py` (append tests)
- Modify: `scripts/convert_obsidian.py` (implement function)

Obsidian image embed syntax: `![[filename.ext|width]]` where `|width` is optional. The `existing` parameter is a set of filenames present in `docs/assets/`. If the file is there, emit an `<img>` tag; if not, emit an HTML comment as a placeholder so the build doesn't crash.

The regex: `!\[\[([^\]|]+?)(?:\|(\d+))?\]\]`
- `([^\]|]+?)` — filename: any chars except `]` and `|`
- `(?:\|(\d+))?` — optional `|digits` group

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_convert_obsidian.py`:

```python


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
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
pytest tests/test_convert_obsidian.py -k image -v
```

Expected: `6 failed` with `NotImplementedError`.

- [ ] **Step 3: Implement `convert_images`**

```python
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
```

- [ ] **Step 4: Run to confirm tests pass**

```bash
pytest tests/test_convert_obsidian.py -k image -v
```

Expected: `6 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/convert_obsidian.py tests/test_convert_obsidian.py
git commit -m "feat: implement convert_images"
```

---

## Task 6: `convert_file` and `main`

**Files:**
- Modify: `tests/test_convert_obsidian.py` (append integration test)
- Modify: `scripts/convert_obsidian.py` (implement `convert_file` and `main`)

`convert_file` orchestrates the four transformations on a single file and writes the result. `main` iterates over every `.md` in `chapters/`. This task uses `pytest`'s `tmp_path` fixture for filesystem isolation — no touching of the real repo dirs.

- [ ] **Step 1: Write the failing integration test**

Append to `tests/test_convert_obsidian.py`:

```python


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
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
pytest tests/test_convert_obsidian.py -k convert_file -v
```

Expected: `2 failed` with `NotImplementedError`.

- [ ] **Step 3: Implement `convert_file` and `main`**

```python
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
```

- [ ] **Step 4: Run all tests to confirm everything passes**

```bash
pytest tests/test_convert_obsidian.py -v
```

Expected: all tests pass (no failures). Count should be 20+.

- [ ] **Step 5: Smoke-test the script against real chapter files**

```bash
cd /path/to/bop
python scripts/convert_obsidian.py
```

Expected output (order may vary by OS sort):
```
  01✓. Sets.md -> 01-sets.md
  02✓. Logic.md -> 02-logic.md
  03✓. Counting.md -> 03-counting.md
```

Check output files exist:
```bash
ls docs/chapters/
```

Expected: `01-sets.md  02-logic.md  03-counting.md`

Spot-check that `==` highlights were converted:
```bash
grep -c "<mark>" docs/chapters/02-logic.md
```

Expected: a number greater than 0 (Logic chapter has several `==...==` highlights).

- [ ] **Step 6: Commit**

```bash
git add scripts/convert_obsidian.py tests/test_convert_obsidian.py
git commit -m "feat: implement convert_file and main orchestrator"
```

---

## Task 7: Sphinx Configuration

**Files:**
- Create: `docs/conf.py`
- Create: `docs/requirements.txt`

No TDD here — these are config files. Verification is done by running `sphinx-build` and checking for errors.

**What each `conf.py` setting does:**
- `myst_enable_extensions = ["dollarmath", ...]` — enables `$...$` math syntax (off by default in MyST 3+; without this, dollar signs render as literal text)
- `html_image` — tells MyST to process `<img>` HTML tags properly instead of passing them through as raw strings
- `colon_fence` — enables `:::` as an alternative to triple-backtick for MyST directives
- `sphinx.ext.mathjax` — injects MathJax JS into every page so LaTeX renders in the browser

- [ ] **Step 1: Install Sphinx dependencies**

```bash
pip install -r docs/requirements.txt
```

- [ ] **Step 2: Create `docs/requirements.txt`**

```
sphinx==9.1.0
furo==2025.12.19
sphinx-copybutton==0.5.2
myst-parser==5.0.0
```

- [ ] **Step 3: Create `docs/conf.py`**

```python
project = "Book of Proof — Annotated"
author = "Richard Hammack (annotations by knnlrts-hq)"
extensions = ["myst_parser", "sphinx_copybutton", "sphinx.ext.mathjax"]
myst_enable_extensions = ["colon_fence", "html_image", "dollarmath"]
html_theme = "furo"
master_doc = "index"
exclude_patterns = ["_build"]
```

- [ ] **Step 4: Run `convert_obsidian.py` to generate `docs/chapters/` (if not already done)**

```bash
python scripts/convert_obsidian.py
```

- [ ] **Step 5: Attempt a Sphinx build (expect failure — index.md doesn't exist yet)**

```bash
sphinx-build -b html docs docs/_build/html 2>&1 | head -20
```

Expected: error mentioning missing `index` document. That's fine — `docs/index.md` is created in the next task.

- [ ] **Step 6: Commit**

```bash
git add docs/conf.py docs/requirements.txt
git commit -m "feat: add Sphinx configuration and pinned requirements"
```

---

## Task 8: `docs/index.md` — Landing Page

**Files:**
- Create: `docs/index.md`

This is the root page of the site. It contains a brief intro to the book and a `{toctree}` directive that lists the chapters. The `{toctree}` directive is MyST syntax — it tells Sphinx which pages to include in the navigation and how to order them.

**Important:** paths in `{toctree}` are relative to `docs/` and have **no `.md` extension** — Sphinx adds it automatically.

- [ ] **Step 1: Create `docs/index.md`**

```markdown
# Book of Proof — Annotated

*Book of Proof* is a free, open-source mathematics textbook by **Richard Hammack**
(Virginia Commonwealth University). It introduces students to the language and
methods of mathematical proof — the foundation of every upper-level mathematics
course. The full text is freely available at
[richardhammack.github.io/BookOfProof](https://richardhammack.github.io/BookOfProof/).

This site contains annotated chapter notes and exercise solutions. Annotations
highlight key definitions and theorems, add worked examples, and flag common
pitfalls.

```{toctree}
:maxdepth: 2
:caption: Chapters

chapters/01-sets
chapters/02-logic
chapters/03-counting
```
```

- [ ] **Step 2: Build the site**

```bash
sphinx-build -b html docs docs/_build/html
```

Expected: build completes with `build succeeded` (warnings about missing images are acceptable — those are the `<!-- TODO: missing image -->` comments in the converted files, which won't cause build failures).

If you see `WARNING: document isn't included in any toctree`, that means a file in `docs/chapters/` isn't listed in the toctree. Double-check the filenames match exactly.

- [ ] **Step 3: Open the built site locally**

```bash
open docs/_build/html/index.html
# or on Linux:
xdg-open docs/_build/html/index.html
```

Check:
- The landing page loads with the Furo theme
- The three chapter links appear in the sidebar
- Click into a chapter and verify LaTeX renders (you should see formatted math, not raw `$...$`)
- Verify `<mark>` highlights appear as yellow-highlighted text
- Verify `%%...%%` blocks are absent from the rendered output

- [ ] **Step 4: Commit**

```bash
git add docs/index.md
git commit -m "feat: add landing page with intro and chapter TOC"
```

---

## Task 9: GitHub Actions Deploy Workflow

**Files:**
- Create: `.github/workflows/deploy.yml`

This workflow runs on every push to `main`. It:
1. Installs Python dependencies
2. Runs the conversion script
3. Builds the Sphinx site
4. Pushes the built HTML to the `gh-pages` branch using `peaceiris/actions-gh-pages`

The `gh-pages` branch is created automatically by the action on first run. You then point GitHub Pages at that branch (one-time manual step in repo settings — covered in Task 10).

**Why `contents: write`?** The `peaceiris/actions-gh-pages` action pushes to the `gh-pages` branch, which requires write access to the repo. The `GITHUB_TOKEN` has this scope when `permissions: contents: write` is set.

- [ ] **Step 1: Create `.github/workflows/deploy.yml`**

```bash
mkdir -p .github/workflows
```

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r docs/requirements.txt

      - name: Convert Obsidian to MyST
        run: python scripts/convert_obsidian.py

      - name: Build Sphinx docs
        run: sphinx-build -b html docs docs/_build/html

      - name: Deploy to gh-pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/_build/html
```

- [ ] **Step 2: Commit and push**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: add GitHub Actions deploy workflow"
git push -u origin claude/host-markdown-chapters-Egk2J
```

(Adjust branch name to whatever you're working on. The workflow triggers on push to `main` — pushing a feature branch does not trigger it yet.)

---

## Task 10: End-to-End Verification and GitHub Pages Setup

This task merges to `main`, confirms the CI pipeline runs green, and enables GitHub Pages.

- [ ] **Step 1: Run the full test suite one last time locally**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 2: Confirm `docs/chapters/` is git-ignored**

```bash
git status docs/chapters/
```

Expected: no output (directory is ignored).

- [ ] **Step 3: Open a PR from your branch to `main` and merge it**

After merging, the GitHub Actions workflow triggers automatically.

- [ ] **Step 4: Watch the CI run**

Go to your repo on GitHub → **Actions** tab. You should see a workflow run called "Deploy to GitHub Pages" in progress.

If it fails, click into the run and read the step that failed. Common issues:
- `ModuleNotFoundError: No module named 'myst_parser'` → the `pip install` step failed, check `docs/requirements.txt` path
- `sphinx-build: command not found` → same cause
- `WARNING: document isn't included in any toctree` → a file in `docs/chapters/` is not listed in `docs/index.md`; this is a warning, not an error, and won't fail the build

- [ ] **Step 5: Enable GitHub Pages**

After the workflow succeeds for the first time, the `gh-pages` branch exists.

1. Go to the repo on GitHub → **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Branch: `gh-pages`, folder: `/ (root)`
4. Click **Save**

GitHub will display the URL where your site is published (typically `https://knnlrts-hq.github.io/bop/`).

- [ ] **Step 6: Verify the live site**

Open the published URL. Check:
- Landing page loads with Furo theme and sidebar navigation
- All three chapters are reachable from the sidebar
- LaTeX math renders (not raw `$` signs) — the Sets chapter opens with display math immediately
- Highlighted text (`==...==`) renders as visually highlighted spans
- No `%%...%%` comment blocks are visible anywhere

- [ ] **Step 7: Adding a new chapter in the future**

When you add a new Obsidian chapter file to `chapters/` (e.g. `04✓. Direct Proof.md`):
1. Drop the file in `chapters/`
2. Add one line to `docs/index.md` under `{toctree}`: `chapters/04-direct-proof`
3. Commit and push to `main`
4. The CI pipeline rebuilds and redeploys automatically

---

## Self-Review Notes

- All five transformation functions have full unit test coverage, including edge cases (no match, multiple matches, missing images)
- The integration test (`test_convert_file`) exercises the full pipeline on a realistic input
- `docs/chapters/` is git-ignored — confirmed in Task 1, verified in Task 10 Step 2
- `docs/assets/` is tracked (via `.gitkeep`) and created by the script (`ASSETS_DIR.mkdir(parents=True, exist_ok=True)`)
- MathJax is explicitly enabled via `sphinx.ext.mathjax` and `dollarmath` MyST extension — critical for this math textbook
- The one-time GitHub Pages setup step is documented in Task 10 Step 5
- The "adding a new chapter" workflow is documented in Task 10 Step 7
