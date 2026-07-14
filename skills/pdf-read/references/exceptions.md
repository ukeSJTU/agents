# Exceptions and safe failure handling

## Native text is missing, short, or garbled

1. Use the inspection report to identify the affected pages.
2. Render only those pages to determine whether visible text, a visual-only
   figure, or an unusual layout is involved.
3. Read any still-available native blocks and visual context.
4. In the final response, add a `提取异常` item containing:
   - page number and approximate region;
   - what native extraction returned;
   - what makes the region unreliable;
   - how it limits the answer;
   - confirmation that OCR was not performed.

Never use the exception as permission to guess or OCR missing content.

## Encrypted PDF

If a script reports `PASSWORD_REQUIRED`, ask the user to supply the password.
Use it only for the current command through `--password`; do not print it,
store it in a report, retry guesses, or attempt to bypass protection. Report a
rejected password once and wait for new user input.

## Cannot open, render, or parse the PDF

Report the affected file and the tool's error message in plain language. Do not
repair, rewrite, or convert the PDF because this skill is read-only. If the
user needs recovery, explain that it is outside this skill's scope and ask
whether they want a separate repair workflow.

## A helpful tool is not available

The bundled scripts require only `uv`; `uv run` manages the declared pypdf,
pdfplumber, pypdfium2, and image dependencies in isolated environments.

If `uv` is unavailable, pause and explain that it is required to create an
isolated environment for the bundled reader scripts. Do not install it.

If another external tool or `uvx` command would be helpful, pause before using
it. State the observed gap, exact tool, installation category (`uvx` or system
tool), purpose, and proposed command. Wait for the user's direction.
