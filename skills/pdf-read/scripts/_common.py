"""Shared read-only helpers for the bundled PDF reader scripts.

The entry points use permissively licensed libraries only: pypdf for structure
and quick native text, pdfplumber for detailed text and tables, and pypdfium2
for rendering. This module contains no PDF-writing operations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader


class PdfReadError(RuntimeError):
    """An expected input or access error that should be reported to the user."""


def resolve_pdf_path(path: str | Path) -> Path:
    pdf_path = Path(path).expanduser().resolve()
    if not pdf_path.is_file():
        raise PdfReadError(f"PDF_NOT_FOUND: {pdf_path}")
    return pdf_path


def open_pdf(path: str | Path, password: str | None = None) -> PdfReader:
    """Open a PDF with pypdf, authenticating only with a user-supplied password."""

    pdf_path = resolve_pdf_path(path)
    try:
        reader = PdfReader(str(pdf_path), strict=False)
    except Exception as error:  # Parser exception classes vary by file and pypdf version.
        raise PdfReadError(f"PDF_OPEN_FAILED: {error}") from error

    if reader.is_encrypted:
        if password is None:
            close_pdf(reader)
            raise PdfReadError(
                "PASSWORD_REQUIRED: The PDF is encrypted. Ask the user for a password; "
                "do not attempt to bypass protection."
            )
        try:
            accepted = reader.decrypt(password)
        except Exception as error:
            close_pdf(reader)
            raise PdfReadError(f"PASSWORD_REJECTED: {error}") from error
        if not accepted:
            close_pdf(reader)
            raise PdfReadError("PASSWORD_REJECTED: The supplied PDF password was not accepted.")

    return reader


def close_pdf(reader: PdfReader) -> None:
    close = getattr(reader, "close", None)
    if callable(close):
        close()


def parse_pages(specification: str | None, page_count: int) -> list[int]:
    """Convert a human-friendly, 1-indexed page range into page numbers."""

    if specification is None or specification.strip().lower() in {"", "all"}:
        return list(range(1, page_count + 1))

    pages: list[int] = []
    for item in specification.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            if "-" in item:
                start_text, end_text = item.split("-", 1)
                start, end = int(start_text), int(end_text)
                if end < start:
                    raise ValueError
                candidates = range(start, end + 1)
            else:
                candidates = (int(item),)
        except ValueError as error:
            raise PdfReadError(
                f"INVALID_PAGE_RANGE: {specification!r}. Use values such as '1,3-5'."
            ) from error

        for page_number in candidates:
            if not 1 <= page_number <= page_count:
                raise PdfReadError(
                    f"PAGE_OUT_OF_RANGE: {page_number}; this PDF has {page_count} pages."
                )
            if page_number not in pages:
                pages.append(page_number)

    if not pages:
        raise PdfReadError("EMPTY_PAGE_SELECTION: Select at least one page.")
    return pages


def rect_to_list(rect: Any) -> list[float]:
    """Convert a coordinate iterable to stable JSON values."""

    return [round(float(value), 2) for value in rect]


def text_status(text: str) -> dict[str, Any]:
    """Describe native-text availability without claiming visual text is absent."""

    normalized = text.strip()
    character_count = len(normalized)
    word_count = len(normalized.split())

    warnings: list[str] = []
    if character_count == 0:
        warnings.append("native_text_missing")
    elif character_count < 20:
        warnings.append("very_little_native_text")

    return {
        "character_count": character_count,
        "word_count": word_count,
        "warnings": warnings,
        "visual_review_recommended": bool(warnings),
        "ocr_performed": False,
    }


def emit_json(payload: dict[str, Any], output: str | None = None) -> None:
    """Print JSON or write it to an explicitly requested, non-PDF output path."""

    serialized = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if output is None:
        print(serialized)
        return

    output_path = Path(output).expanduser().resolve()
    if output_path.suffix.lower() == ".pdf":
        raise PdfReadError("READ_ONLY_VIOLATION: Refusing to write a PDF output.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized + "\n", encoding="utf-8")
    print(f"Wrote JSON report: {output_path}")


def fail(error: Exception) -> None:
    """Emit a concise diagnostic suitable for an agent to report to the user."""

    print(str(error), file=sys.stderr)
    raise SystemExit(2)
