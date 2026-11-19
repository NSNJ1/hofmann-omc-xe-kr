#!/usr/bin/env python3
"""Compare complete Co1/Co2/Co3 collinear 5x5 matrices between OUTCARs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from extract_occupation_matrix import parse_outcar


def symmetrize(matrix: np.ndarray) -> np.ndarray:
    return 0.5 * (matrix + matrix.T)


def read_case(label: str, outcar: Path) -> dict[str, object]:
    atoms: dict[str, object] = {}
    for atom in (1, 2, 3):
        up_raw, down_raw = parse_outcar(outcar, atom=atom)
        up = symmetrize(np.asarray(up_raw, dtype=float))
        down = symmetrize(np.asarray(down_raw, dtype=float))
        if up.shape != (5, 5) or down.shape != (5, 5):
            raise ValueError(f"{outcar}: Co{atom} is not a complete 5x5 pair")
        atoms[f"Co{atom}"] = {
            "up": up,
            "down": down,
            "up_eigenvalues": np.linalg.eigvalsh(up),
            "down_eigenvalues": np.linalg.eigvalsh(down),
        }
    return {"label": label, "path": str(outcar.resolve()), "atoms": atoms}


def compare(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    per_atom: dict[str, object] = {}
    total_up_sq = 0.0
    total_down_sq = 0.0
    max_eigenvalue_delta = 0.0
    for atom in ("Co1", "Co2", "Co3"):
        left_atom = left["atoms"][atom]
        right_atom = right["atoms"][atom]
        up_distance = float(np.linalg.norm(left_atom["up"] - right_atom["up"]))
        down_distance = float(np.linalg.norm(left_atom["down"] - right_atom["down"]))
        up_eigen_delta = np.asarray(left_atom["up_eigenvalues"]) - np.asarray(
            right_atom["up_eigenvalues"]
        )
        down_eigen_delta = np.asarray(left_atom["down_eigenvalues"]) - np.asarray(
            right_atom["down_eigenvalues"]
        )
        max_delta = float(max(np.abs(up_eigen_delta).max(), np.abs(down_eigen_delta).max()))
        max_eigenvalue_delta = max(max_eigenvalue_delta, max_delta)
        total_up_sq += up_distance**2
        total_down_sq += down_distance**2
        per_atom[atom] = {
            "up_frobenius": up_distance,
            "down_frobenius": down_distance,
            "up_eigenvalue_l2": float(np.linalg.norm(up_eigen_delta)),
            "down_eigenvalue_l2": float(np.linalg.norm(down_eigen_delta)),
            "max_eigenvalue_delta": max_delta,
            "left_up_eigenvalues": left_atom["up_eigenvalues"].tolist(),
            "right_up_eigenvalues": right_atom["up_eigenvalues"].tolist(),
            "left_down_eigenvalues": left_atom["down_eigenvalues"].tolist(),
            "right_down_eigenvalues": right_atom["down_eigenvalues"].tolist(),
        }
    return {
        "left": left["label"],
        "right": right["label"],
        "joint_up_frobenius": float(np.sqrt(total_up_sq)),
        "joint_down_frobenius": float(np.sqrt(total_down_sq)),
        "max_eigenvalue_delta": max_eigenvalue_delta,
        "per_atom": per_atom,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        action="append",
        required=True,
        metavar="LABEL=OUTCAR",
        help="May be supplied more than once.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cases = []
    for specification in args.case:
        if "=" not in specification:
            parser.error(f"invalid --case value: {specification}")
        label, raw_path = specification.split("=", 1)
        cases.append(read_case(label, Path(raw_path).expanduser()))

    pairwise = []
    for left_index, left in enumerate(cases):
        for right in cases[left_index + 1 :]:
            pairwise.append(compare(left, right))
    public_cases = []
    for case in cases:
        public_cases.append(
            {
                "label": case["label"],
                "path": case["path"],
                "atoms": {
                    atom: {
                        "up_eigenvalues": values["up_eigenvalues"].tolist(),
                        "down_eigenvalues": values["down_eigenvalues"].tolist(),
                    }
                    for atom, values in case["atoms"].items()
                },
            }
        )
    payload = {"cases": public_cases, "pairwise": pairwise}
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
