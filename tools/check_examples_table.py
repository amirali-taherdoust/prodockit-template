#!/usr/bin/env python3
# Copyright (c) 2025-2026 Mark Buckwell and contributors
# SPDX-License-Identifier: MIT

"""Check that the Examples capability table survives template rendering."""

from __future__ import annotations

import argparse
from pathlib import Path

from bs4 import BeautifulSoup, Tag


EXPECTED_HEADER = ["Capability", "Syntax", "Where"]
COMMON_CAPABILITIES = [
    "Citations",
    "Acronyms",
    "Glossary",
    "Cross-references",
    "Figure captions",
    "Table captions",
    "Cell shading",
    "Directory trees",
    "Numbered steps",
]
OPTIONAL_CAPABILITIES = ["Diagrams", "Maths"]
EXPECTED_CAPTION = "prodockit capabilities demonstrated in this document"


def _cell_text(cell: Tag) -> str:
    """Return normalised visible text from a table cell."""

    return " ".join(cell.get_text(" ", strip=True).split())


def check_examples_table(html: str) -> None:
    """Raise ``ValueError`` when the rendered capability table is malformed."""

    soup = BeautifulSoup(html, "html.parser")
    matches: list[Tag] = []
    for table in soup.find_all("table"):
        header = [_cell_text(cell) for cell in table.find_all("th")]
        if header == EXPECTED_HEADER:
            matches.append(table)

    if len(matches) != 1:
        raise ValueError(
            f"expected one {EXPECTED_HEADER!r} table, found {len(matches)}"
        )

    table = matches[0]
    capabilities = [
        _cell_text(row.find_all("td")[0])
        for row in table.find_all("tr")
        if row.find_all("td")
    ]

    missing = [name for name in COMMON_CAPABILITIES if name not in capabilities]
    if missing:
        raise ValueError(f"capability rows escaped the table: {', '.join(missing)}")

    optional_present = [name in capabilities for name in OPTIONAL_CAPABILITIES]
    if any(optional_present) and not all(optional_present):
        raise ValueError("Diagrams and Maths must be included or omitted together")

    figure = table.find_parent("figure", class_="prodockit-table-caption")
    if figure is None:
        raise ValueError("capability table is not wrapped by its table caption")

    caption = figure.find("figcaption")
    if caption is None or EXPECTED_CAPTION not in _cell_text(caption):
        raise ValueError("capability table caption is missing or attached elsewhere")

    raw_rows = []
    for paragraph in soup.find_all("p"):
        text = _cell_text(paragraph)
        if text.startswith("|") and any(
            name in text for name in COMMON_CAPABILITIES + OPTIONAL_CAPABILITIES
        ):
            raw_rows.append(text)
    if raw_rows:
        raise ValueError("capability rows rendered as raw pipe-delimited text")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    args = parser.parse_args()

    check_examples_table(args.html.read_text(encoding="utf-8"))
    print(f"Examples capability table is intact: {args.html}")


if __name__ == "__main__":
    main()
