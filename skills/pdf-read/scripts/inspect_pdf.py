# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf>=6.14,<7",
# ]
# ///

"""Create a read-only, page-level diagnostic report for an electronic PDF."""

from __future__ import annotations

import argparse

from _common import PdfReadError, close_pdf, emit_json, fail, open_pdf, parse_pages, resolve_pdf_path, text_status


def extract_native_text(page) -> str:
    """Prefer pypdf's layout mode, with a compatibility fallback."""

    try:
        return page.extract_text(extraction_mode="layout") or ""
    except TypeError:
        return page.extract_text() or ""


def outline_count(items) -> int:
    total = 0
    for item in items or []:
        if isinstance(item, list):
            total += outline_count(item)
        else:
            total += 1
    return total


def inspect(pdf_path: str, pages_spec: str | None, password: str | None) -> dict:
    reader = open_pdf(pdf_path, password)
    try:
        page_count = len(reader.pages)
        pages = parse_pages(pages_spec, page_count)
        page_reports: list[dict] = []
        flagged_pages: list[int] = []

        for page_number in pages:
            page = reader.pages[page_number - 1]
            status = text_status(extract_native_text(page))
            if status["visual_review_recommended"]:
                flagged_pages.append(page_number)
            box = page.mediabox
            page_reports.append(
                {
                    "page": page_number,
                    "size_points": [round(float(box.width), 2), round(float(box.height), 2)],
                    "rotation": page.rotation,
                    "native_text": status,
                    "embedded_image_count": len(page.images),
                }
            )

        metadata = {
            str(key): str(value)
            for key, value in (reader.metadata or {}).items()
            if value not in (None, "")
        }
        try:
            toc_entries = outline_count(reader.outline)
        except Exception:
            toc_entries = None

        return {
            "operation": "inspect_pdf",
            "read_only": True,
            "ocr_performed": False,
            "source": str(resolve_pdf_path(pdf_path)),
            "page_count": page_count,
            "inspected_pages": pages,
            "metadata": metadata,
            "table_of_contents_entries": toc_entries,
            "pages": page_reports,
            "visual_review_recommended_pages": flagged_pages,
            "notes": [
                "pypdf provides a fast native-text signal. A low count is a reason to inspect the rendered page, not proof that visible text is absent.",
                "No OCR was attempted by this script.",
            ],
        }
    finally:
        close_pdf(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Source PDF to inspect. It is never modified.")
    parser.add_argument("--pages", help="1-indexed pages, for example: 1,3-5. Defaults to all.")
    parser.add_argument("--password", help="Password supplied by the user for an encrypted PDF.")
    parser.add_argument("--output", help="Optional JSON report path. PDF output paths are refused.")
    args = parser.parse_args()

    try:
        emit_json(inspect(args.pdf, args.pages, args.password), args.output)
    except PdfReadError as error:
        fail(error)


if __name__ == "__main__":
    main()
