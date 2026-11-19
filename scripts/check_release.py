#!/usr/bin/env python3
"""Fail closed on forbidden files, private text, or broken release metadata."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv"}
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
FORBIDDEN_NAMES = {
    "POTCAR",
    "WAVECAR",
    "CHGCAR",
    "OCCMATRIX.old",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        sample = path.read_bytes()[:8192]
    except OSError:
        return False
    return b"\x00" not in sample


def private_path_patterns() -> list[re.Pattern[str]]:
    user_root = "C:" + chr(92) + "Users" + chr(92)
    cluster_root = chr(47) + "home" + chr(47) + "nsnj"
    return [
        re.compile(re.escape(user_root), re.I),
        re.compile(re.escape(cluster_root), re.I),
    ]


def secret_patterns() -> list[re.Pattern[str]]:
    return [
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
        re.compile(r"(?i)\b(?:zenodo|github)_token\s*[:=]\s*['\"]?[A-Za-z0-9._-]{16,}"),
    ]


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        rows.append((digest, relative))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-manifest", action="store_true")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    issues: list[str] = []

    required = [
        "README.md",
        "LICENSE",
        "DATA_LICENSE.md",
        "CITATION.cff",
        "data",
        "docs",
        "scripts",
        "tests",
    ]
    for name in required:
        if not (root / name).exists():
            issues.append(f"missing required path: {name}")

    path_patterns = private_path_patterns()
    token_patterns = secret_patterns()
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        if path.name in FORBIDDEN_NAMES or path.name.startswith("POTCAR."):
            issues.append(f"forbidden file: {relative}")
        if path.stat().st_size > 95 * 1024 * 1024:
            issues.append(f"file exceeds GitHub's 95 MiB safety limit: {relative}")
        if path.resolve() == Path(__file__).resolve() or not is_probably_text(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in path_patterns):
            issues.append(f"personal absolute path: {relative}")
        if any(pattern.search(text) for pattern in token_patterns):
            issues.append(f"possible credential: {relative}")

    if not args.skip_manifest:
        manifest = root / "manifest_sha256.txt"
        if not manifest.is_file():
            issues.append("missing manifest_sha256.txt")
        else:
            for expected, relative in parse_manifest(manifest):
                path = root / relative
                if not path.is_file():
                    issues.append(f"manifest file missing: {relative}")
                elif sha256(path) != expected:
                    issues.append(f"manifest hash mismatch: {relative}")

    for path in (root / "scripts").glob("*.py"):
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            issues.append(f"Python syntax error in {path.name}: {result.stderr.strip()}")

    if issues:
        print("Release check failed:")
        for issue in issues:
            print(f" - {issue}")
        return 1

    print(f"Release check passed for {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
