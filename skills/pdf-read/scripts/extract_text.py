# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pdfplumber>=0.11,<0.12",
#   "pypdf>=6.14,<7",
# ]
# ///

"""Extract native PDF text with page and coordinate evidence; never runs OCR."""

from __future__ import annotations

import argparse

import pdfplumber

from _common import PdfReadError, close_pdf, emit_json, fail, open_pdf, parse_pages, resolve_pdf_path, text_status


def bbox(item: dict) -> list[float]:
    return [round(float(item[key]), 2) for key in ("x0", "top", "x1", "bottom")]


def extract_blocks(page) -> list[dict]:
    """Return pdfplumber text lines as compact, location-aware reading blocks."""

    blocks: list[dict] = []
    for line_number, line in enumerate(page.extract_text_lines(return_chars=False), start=1):
        text = str(line.get("text", "")).strip()
        if not text:
            continue
        blocks.append({"bbox": bbox(line), "text": text, "line_number": line_number})
    return blocks


def extract_words(page) -> list[dict]:
    words: list[dict] = []
    for word_number, word in enumerate(page.extract_words(), start=1):
        words.append({"bbox": bbox(word), "text": str(word["text"]), "word_number": word_number})
    return words


def extract(pdf_path: str, pages_spec: str | None, password: str | None, mode: str) -> dict:
    reader = open_pdf(pdf_path, password)
    try:
        pages = parse_pages(pages_spec, len(reader.pages))
    finally:
        close_pdf(reader)

    try:
        pdf = pdfplumber.open(pdf_path, password=password)
    except Exception as error:
        raise PdfReadError(f"PDFPLUMBER_OPEN_FAILED: {error}") from error

    with pdf:
        reports: list[dict] = []
        for page_number in pages:
            page = pdf.pages[page_number - 1]
            text = page.extract_text() or ""
            report = {"page": page_number, "native_text": text_status(text)}
            if mode == "text":
                report["text"] = text.strip()
            elif mode == "blocks":
                report["blocks"] = extract_blocks(page)
            else:
                report["words"] = extract_words(page)
            reports.append(report)

    return {
        "operation": "extract_text",
        "read_only": True,
        "ocr_performed": False,
        "source": str(resolve_pdf_path(pdf_path)),
        "mode": mode,
        "pages": reports,
        "notes": [
            "Text is native PDF text only. Empty or suspicious output must be reported, not replaced with OCR.",
            "For multi-column pages or layout-sensitive reading, render the relevant page before relying on text order.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Source PDF to read. It is never modified.")
    parser.add_argument("--pages", help="1-indexed pages, for example: 1,3-5. Defaults to all.")
    parser.add_argument("--password", help="Password supplied by the user for an encrypted PDF.")
    parser.add_argument(
        "--mode",
        choices=("text", "blocks", "words"),
        default="blocks",
        help="Evidence detail. 'blocks' is the default for normal reading.",
    )
    parser.add_argument("--output", help="Optional JSON report path. PDF output paths are refused.")
    args = parser.parse_args()

    try:
        emit_json(extract(args.pdf, args.pages, args.password, args.mode), args.output)
    except PdfReadError as error:
        fail(error)


if __name__ == "__main__":
    main()
