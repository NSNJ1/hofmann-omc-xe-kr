#!/usr/bin/env python3
"""Recalculate the load-bearing numerical claims for the merged JCTC paper."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

ENERGY_RE = re.compile(r"energy\(sigma->0\)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[Ee][-+]?\d+)?)")
MAG_RE = re.compile(
    r"number of electron\s+\S+\s+magnetization\s+"
    r"([-+]?\d+(?:\.\d*)?(?:[Ee][-+]?\d+)?)"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def final_energy(path: Path) -> float:
    values = ENERGY_RE.findall(path.read_text(errors="ignore"))
    if not values:
        raise ValueError(f"no energy(sigma->0) in {path}")
    return float(values[-1])


def final_magnetization(path: Path) -> float:
    values = MAG_RE.findall(path.read_text(errors="ignore"))
    if not values:
        raise ValueError(f"no total magnetization in {path}")
    return float(values[-1])


def rounded(value: float, digits: int = 6) -> float:
    return float(f"{value:.{digits}f}")


def reference_distances(text: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in text.split(";"):
        if ":" not in item:
            continue
        label, value = item.split(":", 1)
        result[label.strip()] = float(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    raw = repo / "data" / "raw_text_outputs" / "co3" / "selected"
    closeout = repo / "data" / "source_tables" / "hofmann_closeout"

    selectivity_rows = read_csv(closeout / "standard_selectivity.csv")
    branch_rows = read_csv(closeout / "standard_eads_branches.csv")
    highcut_rows = read_csv(closeout / "highcut_Mx_eads_20261022.csv")
    highcut_complex_rows = read_csv(closeout / "highcut_complex_results.csv")
    complex_state_rows = read_csv(closeout / "standard_complex_states.csv")
    bare_state_rows = read_csv(closeout / "standard_bare_states.csv")

    selectivity = {
        (row["metal"], row["branch"]): float(row["selectivity_xe_minus_kr_meV"])
        for row in selectivity_rows
    }
    ranking = {}
    for branch in sorted({row["branch"] for row in selectivity_rows}):
        ranked = sorted(
            (
                (metal, value)
                for (metal, current_branch), value in selectivity.items()
                if current_branch == branch
            ),
            key=lambda item: item[1],
        )
        ranking[branch] = [metal for metal, _ in ranked]

    selectivity_state_shift = {
        metal: rounded(selectivity[(metal, "Mx")] - selectivity[(metal, "control")])
        for metal in ("Pd", "Pt", "Ni")
    }

    control_same_protocol = {
        (row["metal"], row["gas"]): float(row["same_protocol_eads_meV"])
        for row in branch_rows
        if row["branch"] == "control"
    }
    mx_same_protocol = {
        (row["metal"], row["gas"]): float(row["same_protocol_eads_meV"])
        for row in branch_rows
        if row["branch"] == "Mx"
    }
    selectivity_same_protocol_control = {
        metal: rounded(
            (mx_same_protocol[(metal, "Xe")] - mx_same_protocol[(metal, "Kr")])
            - (control_same_protocol[(metal, "Xe")] - control_same_protocol[(metal, "Kr")])
        )
        for metal in ("Pd", "Pt", "Ni")
    }

    mx_complex_distances = [
        float(row["full_matrix_distance_to_target"])
        for row in complex_state_rows
        if row["target_label"] == "Mx"
    ]
    mx_bare_distances = [
        float(row["full_matrix_distance_to_target"])
        for row in bare_state_rows
        if row["target_label"].upper() == "MX"
    ]
    mx_family_margins = []
    for row in highcut_complex_rows:
        if row["stage"] != "stage2_release" or row["nearest_reference"].upper() != "MX":
            continue
        distances = reference_distances(row["all_reference_distances"])
        target = distances.get("Mx")
        others = [value for label, value in distances.items() if label != "Mx"]
        if target and others:
            mx_family_margins.append(min(others) / target)

    mx_branches = [row for row in branch_rows if row["branch"] == "Mx"]
    complex_shift = [float(row["complex_state_shift_meV"]) for row in mx_branches]
    bare_shift = [float(row["bare_state_shift_meV"]) for row in mx_branches]
    net_eads_shift = [
        float(row["eads_meV"])
        - next(
            float(control["eads_meV"])
            for control in branch_rows
            if control["branch"] == "control"
            and control["metal"] == row["metal"]
            and control["gas"] == row["gas"]
        )
        for row in mx_branches
    ]

    standard_mx = {}
    for row in branch_rows:
        if row["branch"] == "Mx":
            standard_mx[(row["metal"], row["gas"])] = float(row["eads_meV"])

    highcut_shift = []
    for row in highcut_rows:
        key = (row["metal"], row["gas"])
        highcut_shift.append(float(row["eads_meV"]) - standard_mx[key])

    co3_paths = {
        name: raw / name / "OUTCAR"
        for name in (
            "new_333_600",
            "ref701_333_600",
            "control_333_600",
            "new_444_650",
            "ref701_444_650",
            "control_444_650",
        )
    }

    co3_energies = {}
    for name, path in co3_paths.items():
        if path.is_file():
            co3_energies[name] = rounded(final_energy(path), 8)

    co3_control_path = repo / "data" / "source_tables" / "co3" / "CONTROL_LOW_POSTRELAX_GATE.json"
    co3_control = json.loads(co3_control_path.read_text(encoding="utf-8"))

    report: dict[str, Any] = {
        "sources": {
            "standard_selectivity": (closeout / "standard_selectivity.csv")
            .relative_to(repo)
            .as_posix(),
            "standard_eads_branches": (closeout / "standard_eads_branches.csv")
            .relative_to(repo)
            .as_posix(),
            "highcut_Mx": (closeout / "highcut_Mx_eads_20261022.csv").relative_to(repo).as_posix(),
            "co3_control_gate": co3_control_path.relative_to(repo).as_posix(),
        },
        "merged_jctc_claims": {
            "occupation_state_selectivity_order": ranking,
            "Mx_minus_control_selectivity_meV": selectivity_state_shift,
            "Mx_minus_same_protocol_control_selectivity_meV": (selectivity_same_protocol_control),
            "Pd_Pt_anchored_control_selectivity_shift_range_meV": [
                rounded(min(selectivity_state_shift["Pd"], selectivity_state_shift["Pt"])),
                rounded(max(selectivity_state_shift["Pd"], selectivity_state_shift["Pt"])),
            ],
            "Pd_Pt_same_protocol_control_selectivity_shift_range_meV": [
                rounded(
                    min(
                        selectivity_same_protocol_control["Pd"],
                        selectivity_same_protocol_control["Pt"],
                    )
                ),
                rounded(
                    max(
                        selectivity_same_protocol_control["Pd"],
                        selectivity_same_protocol_control["Pt"],
                    )
                ),
            ],
            "Mx_complex_energy_shift_range_meV": [
                rounded(min(complex_shift)),
                rounded(max(complex_shift)),
            ],
            "Mx_bare_state_shift_range_meV": [
                rounded(min(bare_shift)),
                rounded(max(bare_shift)),
            ],
            "Mx_net_eads_shift_range_meV": [
                rounded(min(net_eads_shift)),
                rounded(max(net_eads_shift)),
            ],
            "highcut_650_minus_600_Mx_eads_range_meV": [
                rounded(min(highcut_shift)),
                rounded(max(highcut_shift)),
            ],
            "six_hundred_eV_Ni_Pt_Kr_gap_meV": rounded(
                abs(standard_mx[("Ni", "Kr")] - standard_mx[("Pt", "Kr")])
            ),
            "protocol_to_max_ch3_response_ratio": rounded(147.0 / 48.58),
            "full_matrix_distance_to_common_Mx_target": {
                "complex_min": rounded(min(mx_complex_distances)),
                "complex_max": rounded(max(mx_complex_distances)),
                "bare_min": rounded(min(mx_bare_distances)),
                "bare_max": rounded(max(mx_bare_distances)),
                "complex_values": [rounded(value) for value in mx_complex_distances],
                "bare_values": [rounded(value) for value in mx_bare_distances],
            },
            "Mx_target_family_diagonal_margin": {
                "minimum_second_best_over_best": rounded(min(mx_family_margins)),
                "maximum_second_best_over_best": rounded(max(mx_family_margins)),
                "values": [rounded(value) for value in mx_family_margins],
            },
            "common_Mx_target_scope": (
                "One Ni-Kr target matrix was used for all metals and gases; "
                "these are operational target-family assignments, not "
                "cross-metal identity of complete 5x5 matrices."
            ),
        },
        "co3_second_framework": {
            "energies_eV": co3_energies,
            "new_minus_ref701_333_600_meV": rounded(
                (co3_energies["new_333_600"] - co3_energies["ref701_333_600"]) * 1000
            ),
            "new_minus_ref701_444_650_meV": rounded(
                (co3_energies["new_444_650"] - co3_energies["ref701_444_650"]) * 1000
            ),
            "new_minus_control_333_600_meV": rounded(
                (co3_energies["new_333_600"] - co3_energies["control_333_600"]) * 1000
            ),
            "control_high_setting_identity_preserved": False,
            "control_high_setting_matrix_distance_versus_low_control": {
                "up": co3_control["matrix_comparison"]["versus_low_control_333_600"][
                    "joint_up_frobenius"
                ],
                "down": co3_control["matrix_comparison"]["versus_low_control_333_600"][
                    "joint_down_frobenius"
                ],
            },
        },
    }

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
