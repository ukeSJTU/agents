# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pdfplumber>=0.11,<0.12",
#   "pypdf>=6.14,<7",
# ]
# ///

"""Extract tables from electronic PDFs without changing the source document."""

from __future__ import annotations

import argparse
from typing import Any

import pdfplumber

from _common import PdfReadError, close_pdf, emit_json, fail, open_pdf, parse_pages, rect_to_list, resolve_pdf_path


def normalized_rows(rows: list[list[Any]] | None) -> list[list[str]]:
    return [["" if cell is None else str(cell).strip() for cell in row] for row in (rows or [])]


def tables_to_markdown(tables: list[dict]) -> str:
    chunks: list[str] = []
    for table in tables:
        chunks.append(f"## 第 {table['page']} 页，表 {table['table']}（pdfplumber）")
        rows = table["rows"]
        if not rows:
            chunks.append("_检测到表格区域，但没有提取出单元格内容。_")
            continue
        width = max(len(row) for row in rows)
        prepared = [row + [""] * (width - len(row)) for row in rows]
        header = prepared[0]
        chunks.append("| " + " | ".join(cell.replace("|", "\\|") for cell in header) + " |")
        chunks.append("| " + " | ".join("---" for _ in header) + " |")
        for row in prepared[1:]:
            chunks.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(chunks)


def extract(pdf_path: str, pages_spec: str | None, password: str | None, output_format: str) -> dict:
    reader = open_pdf(pdf_path, password)
    try:
        pages = parse_pages(pages_spec, len(reader.pages))
    finally:
        close_pdf(reader)

    try:
        pdf = pdfplumber.open(pdf_path, password=password)
    except Exception as error:
        raise PdfReadError(f"PDFPLUMBER_OPEN_FAILED: {error}") from error

    tables: list[dict] = []
    with pdf:
        for page_number in pages:
            page = pdf.pages[page_number - 1]
            for table_index, table in enumerate(page.find_tables(), start=1):
                tables.append(
                    {
                        "page": page_number,
                        "table": table_index,
                        "engine": "pdfplumber",
                        "bbox": rect_to_list(table.bbox),
                        "rows": normalized_rows(table.extract()),
                    }
                )

    payload = {
        "operation": "extract_tables",
        "read_only": True,
        "ocr_performed": False,
        "source": str(resolve_pdf_path(pdf_path)),
        "pages": pages,
        "tables": tables,
        "visual_review_recommended": bool(tables),
        "notes": [
            "pdfplumber is the detailed table path. A detected table still requires page-image verification before reporting values or headers.",
            "No detected table does not prove that the page has no visual table.",
            "No OCR was attempted by this script.",
        ],
    }
    if output_format == "markdown":
        payload["markdown"] = tables_to_markdown(tables)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Source PDF to read. It is never modified.")
    parser.add_argument("--pages", help="1-indexed pages, for example: 1,3-5. Defaults to all.")
    parser.add_argument("--password", help="Password supplied by the user for an encrypted PDF.")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Include a Markdown representation in addition to structured JSON.",
    )
    parser.add_argument("--output", help="Optional JSON report path. PDF output paths are refused.")
    args = parser.parse_args()

    try:
        emit_json(extract(args.pdf, args.pages, args.password, args.format), args.output)
    except PdfReadError as error:
        fail(error)


if __name__ == "__main__":
    main()
