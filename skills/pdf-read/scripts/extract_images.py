# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf[image]>=6.14,<7",
# ]
# ///

"""Extract embedded raster images from selected PDF pages with page evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import PdfReadError, close_pdf, fail, open_pdf, parse_pages, resolve_pdf_path


def image_size(image_file) -> tuple[int | None, int | None]:
    try:
        width, height = image_file.image.size
        return int(width), int(height)
    except Exception:
        return None, None


def extract_images(
    pdf_path: str,
    pages_spec: str | None,
    password: str | None,
    output_dir: str,
    min_pixels: int,
) -> dict:
    if min_pixels < 0:
        raise PdfReadError("INVALID_MIN_PIXELS: The value must be zero or greater.")

    destination = Path(output_dir).expanduser().resolve()
    if destination.suffix.lower() == ".pdf":
        raise PdfReadError("READ_ONLY_VIOLATION: Output directory cannot be a PDF path.")
    destination.mkdir(parents=True, exist_ok=True)

    reader = open_pdf(pdf_path, password)
    try:
        pages = parse_pages(pages_spec, len(reader.pages))
        extracted: list[dict] = []
        for page_number in pages:
            page = reader.pages[page_number - 1]
            for image_index, image_file in enumerate(page.images, start=1):
                width, height = image_size(image_file)
                if width is not None and height is not None and width * height < min_pixels:
                    continue

                original_name = str(image_file.name)
                extension = Path(original_name).suffix or ".bin"
                output_path = destination / f"page-{page_number:04d}-image-{image_index:03d}{extension}"
                output_path.write_bytes(image_file.data)
                extracted.append(
                    {
                        "page": page_number,
                        "image_name": original_name,
                        "path": str(output_path),
                        "width": width,
                        "height": height,
                        "format": extension.lstrip("."),
                    }
                )

        return {
            "operation": "extract_images",
            "read_only": True,
            "source": str(resolve_pdf_path(pdf_path)),
            "pages": pages,
            "min_pixels": min_pixels,
            "images": extracted,
            "notes": [
                "pypdf extracts embedded raster data. It records the source page but not a reliable visual bounding box for every PDF image object.",
                "Render the page when image position, caption, vector artwork, or surrounding context matters.",
                "The source PDF was not modified.",
            ],
        }
    finally:
        close_pdf(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Source PDF to inspect. It is never modified.")
    parser.add_argument("output_dir", help="Directory for extracted image artifacts.")
    parser.add_argument("--pages", help="1-indexed pages, for example: 1,3-5. Defaults to all.")
    parser.add_argument("--password", help="Password supplied by the user for an encrypted PDF.")
    parser.add_argument(
        "--min-pixels",
        type=int,
        default=0,
        help="Skip images smaller than this pixel count when dimensions are available. Default: 0 (keep all).",
    )
    args = parser.parse_args()

    try:
        print(
            json.dumps(
                extract_images(args.pdf, args.pages, args.password, args.output_dir, args.min_pixels),
                ensure_ascii=False,
                indent=2,
            )
        )
    except PdfReadError as error:
        fail(error)


if __name__ == "__main__":
    main()
