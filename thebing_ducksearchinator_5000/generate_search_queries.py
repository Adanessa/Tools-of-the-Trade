#!/usr/bin/env python3
"""
generate_search_queries.py

Reads a CSV of Local Authority names, generates search‐query strings
for both Bing and DuckDuckGo, and writes them out.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List

from helpers.paths import get_data_dirs

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# Default CSV column to read. Change this if your header name ever changes.
CSV_FIELD_DEFAULT = "LA (name)"

# Patterns into which each LA name will be interpolated
SEARCH_PATTERNS = [
    "list of nursery schools in {}",
    "nursery schools contact list {}",
    "nursery schools directory {}",
    "nursery schools csv download {}",
    "nursery schools xlsx file {}",
    "nursery schools data download {}",
    "nursery schools pdf download {}",
    "nursery providers {}",
    "early years providers {}",
    "early years providers csv download {}",
    "early years providers xlsx {}",
    "local authority nurseries {}",
    "nursery schools email addresses {}",
    "list of preschools {}",
    "nursery school websites {}",
    "nursery schools database {}",
    "find a nursery {}",
    "directory records {}"
]

# ─── LOAD & VALIDATION ─────────────────────────────────────────────────────────

def load_la_names(csv_path: Path, field_name: str) -> List[str]:
    """
    Read the given CSV, pull every non‐empty value from column `field_name`,
    dedupe, and return a sorted list.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        # Protect against BOM on very first header
        headers = [h.lstrip("\ufeff") for h in headers]

        # Case‐insensitive match
        candidates = [h for h in headers if h.lower() == field_name.lower()]
        if not candidates:
            raise KeyError(f"No '{field_name}' column in CSV. Found: {headers}")

        real_header = candidates[0]
        names = [
            row.get(real_header, "").strip()
            for row in reader
            if row.get(real_header, "").strip()
        ]

    return sorted(set(names))


# ─── QUERY GENERATION & OUTPUT ─────────────────────────────────────────────────

def generate_queries(names: List[str]) -> List[str]:
    """
    For each name, plug it into every SEARCH_PATTERNS template.
    """
    return [pattern.format(name) for name in names for pattern in SEARCH_PATTERNS]


def write_queries(queries: List[str], out_path: Path):
    """
    Write one query per line into `out_path`, creating parent dirs if needed.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(queries), encoding="utf-8")


# ─── MAIN & CLI ────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Generate Bing/DuckDuckGo search queries from an LA CSV."
    )
    p.add_argument(
        "-i", "--input",
        type=Path,
        help="Path to your CSV (must have an 'LA (name)' column).",
        default=None
    )
    p.add_argument(
        "--column",
        help="Exact header name of the column to read.",
        default=CSV_FIELD_DEFAULT
    )
    p.add_argument(
        "--bing-out",
        type=Path,
        help="Where to write Bing queries.",
        default=None
    )
    p.add_argument(
        "--duck-out",
        type=Path,
        help="Where to write DuckDuckGo queries.",
        default=None
    )
    return p.parse_args()


def main():
    dirs = get_data_dirs()

    args = parse_args()

    # If user didn’t give -i, use the default dirty_data/test_data.csv
    input_csv = args.input or (dirs["dirty_data"] / "test_data.csv")

    # If user didn’t override outputs, use the standard queries folder
    bing_out = args.bing_out or (dirs["queries"] / "bing_search_queries.txt")
    duck_out = args.duck_out or (dirs["queries"] / "duckduckgo_search_queries.txt")

    try:
        la_names = load_la_names(input_csv, args.column)
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if not la_names:
        print("⚠️ No names found in CSV – nothing to do.", file=sys.stderr)
        sys.exit(1)

    queries = generate_queries(la_names)
    # remove any accidental duplicates
    queries = list(dict.fromkeys(queries))

    write_queries(queries, bing_out)
    write_queries(queries, duck_out)

    print(f"✅ {len(queries)} queries written:")
    print(f"   • Bing       → {bing_out}")
    print(f"   • DuckDuckGo → {duck_out}")


if __name__ == "__main__":
    main()
