# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf>=6.14,<7",
#   "pypdfium2>=5.8,<6",
#   "pillow>=10,<12",
# ]
# ///

"""Render selected PDF pages to PNG files for visual reading and verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pypdfium2 as pdfium

from _common import PdfReadError, close_pdf, fail, open_pdf, parse_pages, resolve_pdf_path


def close_quietly(resource) -> None:
    close = getattr(resource, "close", None)
    if callable(close):
        close()


def render(
    pdf_path: str,
    pages_spec: str | None,
    password: str | None,
    output_dir: str,
    dpi: int,
) -> dict:
    if not 72 <= dpi <= 600:
        raise PdfReadError("INVALID_DPI: Choose a value from 72 through 600.")

    destination = Path(output_dir).expanduser().resolve()
    if destination.suffix.lower() == ".pdf":
        raise PdfReadError("READ_ONLY_VIOLATION: Output directory cannot be a PDF path.")
    destination.mkdir(parents=True, exist_ok=True)

    reader = open_pdf(pdf_path, password)
    try:
        pages = parse_pages(pages_spec, len(reader.pages))
    finally:
        close_pdf(reader)

    try:
        document = pdfium.PdfDocument(str(resolve_pdf_path(pdf_path)), password=password)
    except Exception as error:
        raise PdfReadError(f"PDFIUM_OPEN_FAILED: {error}") from error

    try:
        rendered: list[dict] = []
        for page_number in pages:
            page = document[page_number - 1]
            bitmap = None
            try:
                bitmap = page.render(scale=dpi / 72)
                output_path = destination / f"page-{page_number:04d}.png"
                bitmap.to_pil().save(output_path)
                rendered.append(
                    {
                        "page": page_number,
                        "path": str(output_path),
                        "width": bitmap.width,
                        "height": bitmap.height,
                    }
                )
            finally:
                if bitmap is not None:
                    close_quietly(bitmap)
                close_quietly(page)

        return {
            "operation": "render_pages",
            "read_only": True,
            "source": str(resolve_pdf_path(pdf_path)),
            "dpi": dpi,
            "rendered_pages": rendered,
            "notes": [
                "PNG files are derived inspection artifacts; pypdfium2 rendered the source without modifying it.",
                "Use rendered pages to verify visual text, charts, formulas, tables, and reading order.",
            ],
        }
    finally:
        close_quietly(document)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Source PDF to render. It is never modified.")
    parser.add_argument("output_dir", help="Directory for generated PNG inspection images.")
    parser.add_argument("--pages", help="1-indexed pages, for example: 1,3-5. Defaults to all.")
    parser.add_argument("--password", help="Password supplied by the user for an encrypted PDF.")
    parser.add_argument("--dpi", type=int, default=200, help="Rendering resolution from 72 to 600. Default: 200.")
    args = parser.parse_args()

    try:
        print(json.dumps(render(args.pdf, args.pages, args.password, args.output_dir, args.dpi), ensure_ascii=False, indent=2))
    except PdfReadError as error:
        fail(error)


if __name__ == "__main__":
    main()
