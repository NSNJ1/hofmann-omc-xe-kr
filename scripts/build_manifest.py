#!/usr/bin/env python3
"""Write SHA-256 manifests for the GitHub and archival release trees."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files_for_manifest(root: Path, include_tiff: bool) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.name.startswith("manifest_sha256"):
            continue
        if not include_tiff and path.suffix.lower() == ".tiff":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def write_manifest(root: Path, output: Path, include_tiff: bool) -> int:
    lines = [
        f"{sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in files_for_manifest(root, include_tiff)
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.expanduser().resolve()

    github_count = write_manifest(
        root,
        root / "manifest_sha256.txt",
        include_tiff=False,
    )
    archive_count = write_manifest(
        root,
        root / "manifest_sha256_zenodo.txt",
        include_tiff=True,
    )
    print(f"GitHub manifest: {github_count} files")
    print(f"Archive manifest: {archive_count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
