#!/usr/bin/env python3
"""Replace local workstation and cluster path prefixes in released text."""

from __future__ import annotations

import argparse
from pathlib import Path

TEXT_SUFFIXES = {
    "",
    ".cff",
    ".csv",
    ".json",
    ".log",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def replacements() -> list[tuple[str, str]]:
    slash = chr(92)
    desktop = "C:" + slash + "Users" + slash + "ftx22" + slash + "Desktop" + slash
    cluster = chr(47) + "home" + chr(47) + "nsnj" + chr(47)
    return [
        (desktop + "JCTC_npj_OMC_20261020" + slash + "03_OMC_ROLP_pilot" + slash, "source:/"),
        (desktop, "source:/"),
        (cluster, "remote:/"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    changed = 0

    for path in root.rglob("*"):
        if not path.is_file() or path.resolve() == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        raw = path.read_bytes()
        if b"\x00" in raw[:8192]:
            continue
        text = raw.decode("utf-8", errors="ignore")
        updated = text
        for old, new in replacements():
            updated = updated.replace(old, new)
        if updated != text:
            changed += 1
            print(path.relative_to(root).as_posix())
            if args.apply:
                path.write_text(updated, encoding="utf-8")

    verb = "changed" if args.apply else "would change"
    print(f"{changed} files {verb}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
