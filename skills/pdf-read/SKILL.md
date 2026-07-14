---
name: pdf-read
description: >-
  Read, review, summarize, search, compare, or answer questions about PDF files.
  Use this skill whenever the user attaches, names, or refers to a PDF and wants
  its native text, tables, images, charts, formulas, layout, or page-specific
  evidence understood—even when they only ask for a summary or a factual answer.
  This is a read-only, no-OCR skill: never create, edit, merge, annotate, fill,
  decrypt by bypass, or otherwise modify PDFs.
compatibility: Requires `uv` on PATH. Bundled scripts use pypdf for structure, pdfplumber for detailed text and tables, and pypdfium2 for rendering; they run with `uv run` and require no OCR or system PDF tools.
---

# Read PDFs with page-level evidence

## Scope and operating principles

Use this skill to understand an existing PDF. Treat the source PDF as immutable.
It may produce JSON, Markdown table data, PNG renders, and extracted image
files, but it never writes a PDF or uses OCR.

Prefer native PDF content because the user's PDFs are normally electronic.
Native text is often more accurate than OCR and preserves coordinates. If a page
or visible region appears to contain text but native extraction is empty,
suspiciously short, or garbled, report it as an extraction exception. Do not
silently omit it, infer its contents, or replace it with OCR.

## Runtime policy

1. Resolve the absolute path to this skill directory as `SKILL_DIR` before
   running a bundled script. Use its absolute script path; do not copy scripts
   into the user's project.
2. Check that `uv` is available. If it is not, pause and tell the user that the
   bundled read-only scripts need `uv`, why it is needed, and how they can
   install it. Do not install it automatically.
3. Run bundled scripts only with `uv run`. Their inline metadata installs the
   declared Python dependencies in uv-managed environments without changing the
   user's global Python packages.
4. Do not invoke `uvx`, Homebrew, apt, or another unbundled CLI automatically.
   If a task would genuinely benefit from one, pause first and state: the
   missing capability, the specific tool, why it is needed, whether it is an
   `uvx` or system installation, and the proposed command. Wait for direction.
5. Keep derived artifacts in a session-owned temporary directory or an explicit
   user-selected output directory. Never overwrite user files. Do not delete
   artifacts the user asked to keep.

Example setup for an invocation:

```bash
SKILL_DIR="/absolute/path/to/pdf-read"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pdf-read.XXXXXX")"
uv run "$SKILL_DIR/scripts/inspect_pdf.py" "$PDF_PATH" --output "$WORK_DIR/inspect.json"
```

## Default workflow

### 1. Inspect before interpreting

Run `inspect_pdf.py` for every PDF before making claims from it:

```bash
uv run "$SKILL_DIR/scripts/inspect_pdf.py" "$PDF_PATH" --output "$WORK_DIR/inspect.json"
```

Use its page count, native-text diagnostics, image count, drawing count, and
table-of-contents signal to choose the relevant pages and reading path. A low
text count only signals that visual review may be needed; it is not proof that
the page has no visible text.

If the PDF requires a password, ask the user for it. Use `--password` only when
they supply one, do not echo it in the response, and do not retain it after the
operation. If the password is rejected, report that fact without retrying
guesses.

### 2. Select the smallest useful reading path

| User need or PDF condition                                       | Read this reference                                  | Use these scripts                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| Narrative text, search, summary, quotation, comparison           | [references/text.md](references/text.md)             | `extract_text.py`; render only when layout needs checking              |
| Charts, diagrams, formulas, screenshots, or page appearance      | [references/visuals.md](references/visuals.md)       | `render_pages.py`; use `extract_images.py` only for embedded originals |
| Tables, figures with data, or rows and columns                   | [references/tables.md](references/tables.md)         | `extract_tables.py`, then `render_pages.py` for verification           |
| Empty/garbled text, password, malformed file, or missing runtime | [references/exceptions.md](references/exceptions.md) | `inspect_pdf.py`, then render the affected pages                       |
| Questions about `uv`, a new CLI, output locations, or licensing  | [references/runtime.md](references/runtime.md)       | No extra tool without user direction                                   |

Read only the reference files needed for the request. For example, a short
single-column summary usually needs `text.md`, not the table and visuals
references.

### 3. Preserve evidence while reading

Use page numbers in all substantive findings. For text, prefer `blocks` mode so
each passage retains a bounding box:

```bash
uv run "$SKILL_DIR/scripts/extract_text.py" "$PDF_PATH" --pages "2-4" --mode blocks --output "$WORK_DIR/text.json"
```

Do not treat native extraction order as reliable for multi-column pages,
sidebars, complex footnotes, or heavily designed layouts. Render the relevant
page and inspect it before quoting, summarizing, or comparing content whose
order matters.

### 4. Report what was and was not read

State conclusions first, then page evidence. When content could not be
reliably extracted, add a separate exception section rather than hiding the
limitation. Describe the page, approximate visual region where possible, why
the region is uncertain, and its impact on the answer. Explicitly say that no
OCR was performed when that matters.

## Response structure

Use the smallest subset that fits the request. Do not fabricate empty sections.

```markdown
## 结论

<answer, summary, or comparison>

## 依据

- <claim or quotation>（第 N 页；如有需要，说明表格、图号或区域）

## 表格或视觉内容

<only when relevant; include source page and any verification caveat>

## 提取异常

- <only when relevant: page, approximate region, native extraction problem,
  impact, and that OCR was not used>
```

## Non-goals

- Do not create, edit, merge, split, watermark, annotate, fill, sign, encrypt,
  decrypt by bypass, or optimize PDFs.
- Do not OCR pages, images, or regions.
- Do not claim a table, chart, image, or visible text was absent solely because
  one extractor did not return it.
- Do not install or use an unbundled tool without explaining the gap and waiting
  for the user's direction.
