# Native text reading

## Goal

Read electronic PDF text with page-level evidence. The bundled script extracts
only the PDF's native text layer; it does not call OCR or alter the source.

## Choose the evidence detail

Use the least detailed mode that preserves enough evidence for the task:

| Need                                                       | Command mode | Use it for                                                |
| ---------------------------------------------------------- | ------------ | --------------------------------------------------------- |
| Fast orientation or a simple single-column summary         | `text`       | Page-by-page prose with no layout-sensitive quotation     |
| Normal reading, quotations, section comparison             | `blocks`     | Text-line blocks with bounding boxes; this is the default |
| Spatial search, closely positioned labels, custom ordering | `words`      | Individual words with locations                           |

```bash
uv run "$SKILL_DIR/scripts/extract_text.py" "$PDF_PATH" \
  --pages "3-6" --mode blocks --output "$WORK_DIR/text.json"
```

Keep the page number and, when useful, the block bounding box attached to
notes. Never present a quote as exact if the page's extraction order is known
to be unreliable.

## Layout-sensitive pages

Native text can be valid while its order is wrong. Treat these as visual-review
signals:

- two or more narrow columns;
- sidebars, pull quotes, margin notes, or footnotes;
- text wrapping around a large figure;
- headers and footers repeated on each page;
- forms, slides, posters, or pages designed like dashboards.

Render only the relevant page, then compare its appearance with the extracted
blocks:

```bash
uv run "$SKILL_DIR/scripts/render_pages.py" "$PDF_PATH" "$WORK_DIR/pages" \
  --pages "4" --dpi 200
```

Use the visual layout to establish a sensible reading order. Do not silently
remove repeated headers, footers, references, or sidebars: exclude them from a
summary only when their role is clear, and retain their page context if they
matter to the user's question.

## Native-text exceptions

The following are extraction exceptions, not permission to OCR:

- `native_text_missing` on a visually text-bearing page;
- `very_little_native_text` where more readable content is visibly present;
- garbled or implausible characters;
- a reading order that cannot be resolved from text blocks plus the rendered
  page.

In the final response, identify the affected page and region, explain the
impact, and say that OCR was not performed. Do not infer the unextracted words
or use them as evidence.
