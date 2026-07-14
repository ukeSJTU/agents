# Runtime, dependencies, and licensing

## Standard execution

Each entry-point script includes PEP 723 inline metadata. Invoke it with `uv
run`:

```bash
uv run "$SKILL_DIR/scripts/inspect_pdf.py" "$PDF_PATH"
```

This lets uv resolve each script's declared dependencies without adding packages
to the user's global Python environment. Do not use `uv tool install` for these
libraries: they are imported by bundled scripts, not standalone tools expected
on the user's PATH.

## Dependency choices

| Library    | Role                                                                                                                    | Loaded by                                                           |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| pypdf      | Fast PDF structure, metadata, page count, password handling, initial native-text signal, and embedded raster extraction | Inspection, image extraction, and as a preflight for detailed paths |
| pdfplumber | Detailed native text lines and word coordinates; configurable table extraction                                          | `extract_text.py` and `extract_tables.py`                           |
| pypdfium2  | Fast page rendering through PDFium                                                                                      | `render_pages.py`                                                   |
| Pillow     | Saving pypdfium2 renders and accessing pypdf image dimensions                                                           | Rendering and embedded-image extraction                             |

The workflow deliberately uses the lightweight pypdf path first, then applies
pdfplumber only to pages requiring detailed textual or tabular evidence, and
pypdfium2 only where visual validation is necessary. This keeps a long,
electronic PDF fast to inspect without weakening the evidence needed for the
final answer.

## Licence boundary

The bundled direct dependencies use permissive licensing: pypdf is BSD-3-Clause,
pdfplumber is MIT, and pypdfium2 is Apache-2.0 or BSD-3-Clause with additional
PDFium dependency notices. Preserve any applicable third-party notices if this
skill is redistributed. Do not add a copyleft-only PDF engine without reviewing
the repository's licence and distribution model.

## Derived artifacts

JSON reports, PNG renders, and extracted image files are derived read-only
artifacts. Store them in a session-owned temporary directory by default. Keep
them only when the user requests delivery or inspection. Never write a PDF.
