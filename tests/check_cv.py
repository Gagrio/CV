"""Checks on the rendered CV.

Usage: python tests/check_cv.py <cv.yaml> <output-folder>

Settings (environment variables):
  MAX_PAGES      maximum number of pages allowed (default: 2)
  EXPECTED_FONT  font every character should be set in (default: SUSE)
  FALLBACK_OK    characters allowed to come from another font (default: "◦",
                 the Opal theme's bullet, which SUSE doesn't include)
"""

import os
import sys
from collections import Counter
from pathlib import Path

import yaml
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar
from pypdf import PdfReader

ICON_FONTS = ("FontAwesome",)


def chars(layout):
    if isinstance(layout, LTChar):
        yield layout
    elif hasattr(layout, "__iter__"):
        for child in layout:
            yield from chars(child)


def main(cv_file: Path, out_dir: Path) -> int:
    max_pages = int(os.environ.get("MAX_PAGES", "2"))
    font = os.environ.get("EXPECTED_FONT", "SUSE")
    fallback_ok = set(os.environ.get("FALLBACK_OK", "◦"))
    name = yaml.safe_load(cv_file.read_text(encoding="utf-8"))["cv"]["name"]

    errors = []
    pdfs = sorted(out_dir.glob("*.pdf"))
    if len(pdfs) != 1:
        print(f"FAIL expected one PDF in {out_dir}, found {len(pdfs)}")
        return 1
    pdf = pdfs[0]
    reader = PdfReader(pdf)
    pages = len(reader.pages)

    # 1. Length
    if pages > max_pages:
        errors.append(f"{pages} pages, the limit is {max_pages}")

    # 2. One preview image per page
    pngs = list(out_dir.glob("*.png"))
    if len(pngs) != pages:
        errors.append(f"{len(pngs)} PNG previews for {pages} pages")

    # 3. The header carries the right name
    if name not in (reader.pages[0].extract_text() or ""):
        errors.append(f"'{name}' not found on page 1")

    # 4. Text is set in the expected font, not a silent fallback
    fallback = {}
    for page in extract_pages(pdf):
        for ch in chars(page):
            if font in ch.fontname or any(f in ch.fontname for f in ICON_FONTS):
                continue
            if ch.get_text() not in fallback_ok:
                used = ch.fontname.split("+")[-1]
                fallback.setdefault(used, Counter())[ch.get_text()] += 1
    for used, counter in fallback.items():
        sample = " ".join(c for c, _ in counter.most_common(10))
        errors.append(
            f"{sum(counter.values())} characters set in {used} instead of {font}"
            f" (e.g. {sample}) - is the font missing?"
        )

    # 5. Links survived rendering
    links = sum(
        1
        for page in reader.pages
        for annot in page.get("/Annots") or []
        if "/URI" in (annot.get_object().get("/A") or {})
    )
    if links == 0:
        errors.append("no hyperlinks in the PDF")

    print(f"{pdf.name}: {pages} page(s), {len(pngs)} preview(s), {links} link(s)")
    for error in errors:
        print(f"FAIL {error}")
    if not errors:
        print("All checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
