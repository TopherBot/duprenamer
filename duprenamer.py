#!/usr/bin/env python3
"""dupRenamer – tiny duplicate‑file detector & auto‑renamer.

Usage:
    python -m duprenamer [options] <directory>

Options:
    -h, --help      Show this help message and exit.
    -q, --quiet     Suppress the final summary table.
    -v, --verbose   Print each file as it is processed.
    -d, --dry-run   Show what would be renamed without touching the FS.
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_hash(path: Path, chunk_size: int = 65536) -> str:
    """Return SHA‑256 hex digest of *path*.
    Reads the file in *chunk_size* byte chunks to keep memory usage low.
    """
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
    except (OSError, PermissionError) as exc:
        # Quick error recovery – report and continue.
        print(f"[WARN] Cannot read {path}: {exc}", file=sys.stderr)
        return ""
    return h.hexdigest()


def unique_name(original: Path, existing: set) -> Path:
    """Generate a new filename like ``name (1).ext`` that does not clash.
    *existing* is a set of already‑used Path objects (absolute).
    """
    stem = original.stem
    suffix = original.suffix
    counter = 1
    while True:
        candidate = original.with_name(f"{stem} ({counter}){suffix}")
        if candidate.resolve() not in existing:
            return candidate
        counter += 1

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def find_duplicates(root: Path, verbose: bool = False) -> Dict[str, List[Path]]:
    """Walk *root* and return a mapping ``hash → [paths]`` for duplicates.
    Empty hash entries (failed reads) are ignored.
    """
    hash_map: Dict[str, List[Path]] = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if verbose:
                print(f"[INFO] Scanning {fpath}")
            h = compute_hash(fpath)
            if h:
                hash_map[h].append(fpath)
    return {h: lst for h, lst in hash_map.items() if len(lst) > 1}


def rename_duplicates(dup_map: Dict[str, List[Path]], dry_run: bool = False, quiet: bool = False) -> int:
    """Rename duplicate files in‑place.
    Returns the number of files renamed.
    """
    renamed = 0
    for h, paths in dup_map.items():
        # Keep the first occurrence untouched; rename the rest.
        keeper = paths[0].resolve()
        existing = {p.resolve() for p in paths}
        if not quiet:
            print(f"[DUP] {keeper} (kept)")
        for dup in paths[1:]:
            new_path = unique_name(dup, existing)
            if not quiet:
                print(f"[RENAME] {dup} → {new_path}")
            if not dry_run:
                try:
                    dup.replace(new_path)  # atomic on same FS
                except OSError as exc:
                    print(f"[ERROR] Failed to rename {dup}: {exc}", file=sys.stderr)
                    continue
            existing.add(new_path.resolve())
            renamed += 1
    return renamed

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str]):
    parser = argparse.ArgumentParser(description="Detect and auto‑rename duplicate files.")
    parser.add_argument("directory", type=Path, nargs="?", default=Path.cwd(), help="Root folder to scan (default: cwd)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress summary table")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose file processing output")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Show actions without renaming")
    return parser.parse_args(argv)


def main(argv: List[str] = None):
    args = parse_args(argv or sys.argv[1:])
    root = args.directory.resolve()
    if not root.is_dir():
        print(f"[FAIL] {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    dup_map = find_duplicates(root, verbose=args.verbose)
    if not dup_map:
        if not args.quiet:
            print("✅ No duplicates found.")
        return 0

    count = rename_duplicates(dup_map, dry_run=args.dry_run, quiet=args.quiet)
    if not args.quiet:
        print(f"\n📦 {count} file(s) renamed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
