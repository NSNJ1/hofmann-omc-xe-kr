#!/usr/bin/env python3
"""Extract the last collinear 5x5 spin-up/down d occupation matrices from OUTCAR."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][-+]?\d+)?")


def numeric_values(lines: list[str], start: int) -> list[float]:
    values: list[float] = []
    rows = 0
    for line in lines[start + 1 :]:
        numbers = NUM.findall(line)
        if len(numbers) < 5:
            continue
        values.extend(float(x.replace("D", "E").replace("d", "e")) for x in numbers[:5])
        rows += 1
        if rows == 5:
            break
    return values


def matrices_from_window(
    window: list[str],
    source: Path,
) -> tuple[list[list[float]], list[list[float]]]:
    up: list[list[float]] | None = None
    down: list[list[float]] | None = None
    for i, line in enumerate(window):
        low = line.lower().strip()
        if re.search(r"spin\s+component\s+1", low):
            vals = numeric_values(window, i)
            if len(vals) < 25:
                raise ValueError(f"incomplete spin-1 matrix in {source}")
            up = [vals[j : j + 5] for j in range(0, 25, 5)]
        elif re.search(r"spin\s+component\s+2", low):
            vals = numeric_values(window, i)
            if len(vals) < 25:
                raise ValueError(f"incomplete spin-2 matrix in {source}")
            down = [vals[j : j + 5] for j in range(0, 25, 5)]
            if up is not None:
                break
    if up is None or down is None:
        raise ValueError(f"could not find both spin components in {source}")
    return up, down


def atom_matrices(path: Path) -> dict[int, tuple[list[list[float]], list[list[float]]]]:
    text = path.read_text(errors="ignore").splitlines()
    atom_starts: list[tuple[int, int]] = []
    for index, line in enumerate(text):
        match = re.match(r"^\s*atom\s*=\s*(\d+)\s+type\s*=", line, re.I)
        if match:
            atom_starts.append((index, int(match.group(1))))
    matrices: dict[int, tuple[list[list[float]], list[list[float]]]] = {}
    for position, (start, atom) in enumerate(atom_starts):
        end = atom_starts[position + 1][0] if position + 1 < len(atom_starts) else len(text)
        window = text[start:end]
        if not any("onsite density matrix" in line.lower() for line in window):
            continue
        matrices[atom] = matrices_from_window(window, path)
    return matrices


def parse_outcar(
    path: Path,
    atom: int | None = None,
) -> tuple[list[list[float]], list[list[float]]]:
    text = path.read_text(errors="ignore").splitlines()
    if atom is not None:
        matrices = atom_matrices(path)
        if atom not in matrices:
            raise ValueError(f"atom {atom} has no onsite density matrix in {path}")
        return matrices[atom]
    starts = [i for i, line in enumerate(text) if "onsite density matrix" in line.lower()]
    if not starts:
        raise ValueError(f"no onsite density matrix in {path}")
    return matrices_from_window(text[starts[-1] : starts[-1] + 80], path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("outcar", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--atom", type=int)
    args = parser.parse_args()
    up, down = parse_outcar(args.outcar, atom=args.atom)
    if args.json:
        import json

        print(json.dumps({"up": up, "down": down}, indent=2))
    else:
        print("spin component 1")
        for row in up:
            print(" ".join(f"{x:.8f}" for x in row))
        print("spin component 2")
        for row in down:
            print(" ".join(f"{x:.8f}" for x in row))


if __name__ == "__main__":
    main()
