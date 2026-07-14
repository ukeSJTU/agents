# Images, charts, formulas, and page appearance

## Render first when visual context is the content

Use a rendered page when the user asks about charts, diagrams, screenshots,
formula layout, flowcharts, maps, slide-like pages, multi-column arrangement,
or a region whose native text is missing. Rendering preserves the relationship
between labels, marks, and surrounding text.

```bash
uv run "$SKILL_DIR/scripts/render_pages.py" "$PDF_PATH" "$WORK_DIR/pages" \
  --pages "8-9" --dpi 200
```

Use 200 DPI for normal review. Increase to 300 DPI only when labels, formulas,
or fine chart details remain unreadable; avoid rendering an entire long PDF at
high resolution without need.

## Embedded image versus rendered page

These operations solve different problems:

| Need                                                             | Preferred approach         | Why                                                          |
| ---------------------------------------------------------------- | -------------------------- | ------------------------------------------------------------ |
| Understand a chart, diagram, figure label, or formula in context | Render the page            | The visual relationship to its caption and axes is preserved |
| Retain the original raster photo, logo, or screenshot            | Extract the embedded image | Avoids resampling the image through a page render            |
| Understand vector artwork                                        | Render the page            | Vector artwork is not necessarily an embedded raster image   |

Extract original raster images only when the user needs the image itself:

```bash
uv run "$SKILL_DIR/scripts/extract_images.py" "$PDF_PATH" "$WORK_DIR/images" \
  --pages "8"
```

The script records the source page, embedded-image name, and dimensions for
each extracted raster. It does not reliably locate every image object on the
page, extract the surrounding caption, or render vector diagrams.

## Reading visual evidence

Describe what is visible, then connect it to page-local evidence. For a chart,
state the title, axes, legend, units, comparison, and the page number. If a
number or label is not legible, say so instead of estimating it.

If visible labels have no usable native text, record them as an extraction
exception. This skill does not OCR them.
