# Tables

## Extract, then verify

Tables in electronic PDFs can be represented by borders, aligned text, merged
cells, repeated headers, or a mixture of these. Extraction is therefore a
candidate transcription, not automatically authoritative data.

Use the table script for only the pages likely to contain tables:

```bash
uv run "$SKILL_DIR/scripts/extract_tables.py" "$PDF_PATH" \
  --pages "5-7" --format markdown --output "$WORK_DIR/tables.json"
```

The script uses pdfplumber because its configurable, object-level model is the
skill's detailed table path. If a particular table fails, render and inspect the
page before considering any unbundled tool.

## Required visual check

Render each page that contributes a value to the answer:

```bash
uv run "$SKILL_DIR/scripts/render_pages.py" "$PDF_PATH" "$WORK_DIR/pages" \
  --pages "5-7" --dpi 200
```

Compare at least these points against the rendered page:

- table title and units;
- header-to-column alignment;
- merged cells, blanks, and footnotes;
- negative signs, decimals, percentages, and date formats;
- repeated headers and table continuations across pages.

State the source page and table number when reporting a value. If extraction
has an unresolved cell alignment issue, report the uncertainty rather than
forcing a clean table.

## When no table is detected

Do not conclude that a page contains no table solely from an empty result.
Render it. A borderless table, a table inside a figure, or a visually grouped
list may not be detected as a table. If visible tabular content cannot be read
reliably from native structure, record an extraction exception; do not OCR it.
