#!/usr/bin/env python3
"""Analyze the Co3-squarate state-preserving Xe/Kr adsorption pilot."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from extract_occupation_matrix import parse_outcar

ENERGY_RE = re.compile(r"energy\(sigma->0\)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)")
MAG_RE = re.compile(
    r"number of electron\s+\S+\s+magnetization\s+"
    r"([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)"
)


def final_energy(path: Path) -> float:
    values = ENERGY_RE.findall(path.read_text(errors="ignore"))
    if not values:
        raise ValueError(f"No energy(sigma->0) in {path}")
    return float(values[-1].replace("D", "E"))


def final_magnetization(path: Path) -> float:
    values = MAG_RE.findall(path.read_text(errors="ignore"))
    if not values:
        raise ValueError(f"No total magnetization in {path}")
    return float(values[-1].replace("D", "E"))


def symmetrize(matrix: list[list[float]]) -> np.ndarray:
    array = np.asarray(matrix, dtype=float)
    return 0.5 * (array + array.T)


def case_audit(case_dir: Path) -> dict[str, object]:
    stage1 = case_dir / "stage1_omc"
    stage2 = case_dir / "stage2_release"
    outcar = stage2 / "OUTCAR"
    outcar_text = outcar.read_text(errors="ignore")
    stage1_log = (stage1 / "vasp.log").read_text(errors="ignore")
    stage2_incar = (stage2 / "INCAR").read_text(errors="ignore")
    matrices: dict[str, object] = {}
    for atom in range(1, 7):
        up, down = parse_outcar(outcar, atom=atom)
        up_array = symmetrize(up)
        down_array = symmetrize(down)
        matrices[f"Co{atom}"] = {
            "up": up_array,
            "down": down_array,
            "up_eigenvalues": np.linalg.eigvalsh(up_array),
            "down_eigenvalues": np.linalg.eigvalsh(down_array),
        }
    return {
        "case": str(case_dir),
        "energy_eV": final_energy(outcar),
        "total_magnetization_uB": final_magnetization(outcar),
        "stage1_occext_found": "OCCEXT found" in stage1_log,
        "stage2_occext_zero": bool(re.search(r"^\s*OCCEXT\s*=\s*0\s*$", stage2_incar, re.I | re.M)),
        "ediFF_reached": "aborting loop because EDIFF is reached" in outcar_text,
        "nelm_reached": "aborting loop because NELM is reached" in outcar_text,
        "matrices": matrices,
    }


def combined_signature(case: dict[str, object]) -> tuple[np.ndarray, np.ndarray]:
    matrices = case["matrices"]
    up = np.concatenate(
        [np.asarray(matrices[f"Co{atom}"]["up"]).reshape(-1) for atom in range(1, 7)]
    )
    down = np.concatenate(
        [np.asarray(matrices[f"Co{atom}"]["down"]).reshape(-1) for atom in range(1, 7)]
    )
    return up, down


def matrix_comparison(
    left: dict[str, object],
    right: dict[str, object],
) -> dict[str, float]:
    left_up, left_down = combined_signature(left)
    right_up, right_down = combined_signature(right)
    max_eigenvalue_delta = 0.0
    for atom in range(1, 7):
        left_matrices = left["matrices"][f"Co{atom}"]
        right_matrices = right["matrices"][f"Co{atom}"]
        for spin in ("up", "down"):
            left_values = np.asarray(left_matrices[f"{spin}_eigenvalues"])
            right_values = np.asarray(right_matrices[f"{spin}_eigenvalues"])
            max_eigenvalue_delta = max(
                max_eigenvalue_delta,
                float(np.max(np.abs(left_values - right_values))),
            )
    return {
        "joint_up_frobenius": float(np.linalg.norm(left_up - right_up)),
        "joint_down_frobenius": float(np.linalg.norm(left_down - right_down)),
        "max_eigenvalue_delta": max_eigenvalue_delta,
    }


def json_safe_case(case: dict[str, object]) -> dict[str, object]:
    public = {key: value for key, value in case.items() if key != "matrices"}
    public["eigenvalues"] = {
        atom: {
            "up": case["matrices"][atom]["up_eigenvalues"].tolist(),
            "down": case["matrices"][atom]["down_eigenvalues"].tolist(),
        }
        for atom in case["matrices"]
    }
    return public


def write_report(
    root: Path,
    phase: str,
    payload: dict[str, object],
) -> None:
    (root / f"{phase.upper()}_ANALYSIS.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        f"# Co3-squarate adsorption pilot — {phase}",
        "",
        f"- Decision: **{payload['decision']}**",
        f"- Reasons: {'; '.join(payload['reasons']) or 'none'}",
        "",
    ]
    if "bare_state_separation" in payload:
        separation = payload["bare_state_separation"]
        lines.extend(
            [
                "## Bare-state separation",
                "",
                f"- joint up distance: {separation['joint_up_frobenius']:.8f}",
                f"- joint down distance: {separation['joint_down_frobenius']:.8f}",
                f"- max eigenvalue delta: {separation['max_eigenvalue_delta']:.8f}",
                "",
            ]
        )
    if "state_identity" in payload:
        lines.extend(["## Gas-state identity", ""])
        for name, result in payload["state_identity"].items():
            lines.extend(
                [
                    f"### {name}",
                    "",
                    f"- intended distance: {result['intended_distance']:.8f}",
                    f"- alternate distance: {result['alternate_distance']:.8f}",
                    f"- max eigenvalue delta: {result['max_eigenvalue_delta']:.8f}",
                    f"- pass: {result['pass']}",
                    "",
                ]
            )
    if "adsorption" in payload:
        lines.extend(
            [
                "## Adsorption proxy",
                "",
                "```json",
                json.dumps(payload["adsorption"], indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        )
    (root / f"{phase.upper()}_REPORT.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--phase", choices=("phase0", "gas"), required=True)
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    bare = {
        state: case_audit(root / "jobs" / state / "bare") for state in ("new_state", "state701")
    }
    bare_separation = matrix_comparison(bare["new_state"], bare["state701"])
    bare_complete = all(
        case["stage1_occext_found"]
        and case["stage2_occext_zero"]
        and case["ediFF_reached"]
        and not case["nelm_reached"]
        for case in bare.values()
    )
    reasons = []
    if not bare_complete:
        reasons.append("bare supercell did not pass electronic/OMC completion checks")
    if bare_separation["joint_down_frobenius"] < 0.5:
        reasons.append("bare new/701 signatures collapsed in the 1x1x2 supercell")

    if args.phase == "phase0":
        decision = "PASS_TO_GAS_PHASE" if not reasons else "STOP_BARE_STATE_GATE"
        payload = {
            "phase": "phase0",
            "decision": decision,
            "reasons": reasons,
            "bare_state_separation": bare_separation,
            "cases": {state: json_safe_case(case) for state, case in bare.items()},
        }
        write_report(root, "phase0", payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if decision == "PASS_TO_GAS_PHASE" else 2

    complexes = {
        state: {
            gas.lower(): case_audit(root / "jobs" / state / gas.lower()) for gas in ("Xe", "Kr")
        }
        for state in ("new_state", "state701")
    }
    gas_energies = {
        gas.lower(): final_energy(root / "jobs" / "gas" / gas.lower() / "control" / "OUTCAR")
        for gas in ("Xe", "Kr")
    }

    identity = {}
    for state in ("new_state", "state701"):
        alternate = "state701" if state == "new_state" else "new_state"
        for gas in ("xe", "kr"):
            case = complexes[state][gas]
            same = matrix_comparison(case, bare[state])
            other = matrix_comparison(case, bare[alternate])
            passed_common = (
                case["stage1_occext_found"]
                and case["stage2_occext_zero"]
                and case["ediFF_reached"]
                and not case["nelm_reached"]
                and abs(case["total_magnetization_uB"] - 18.0) < 0.1
            )
            passed_identity = (
                same["joint_down_frobenius"] <= 0.15
                and same["max_eigenvalue_delta"] <= 0.01
                and same["joint_down_frobenius"] < other["joint_down_frobenius"]
            )
            identity[f"{state}-{gas}"] = {
                "intended_distance": same["joint_down_frobenius"],
                "alternate_distance": other["joint_down_frobenius"],
                "max_eigenvalue_delta": same["max_eigenvalue_delta"],
                "common_checks_pass": passed_common,
                "pass": passed_common and passed_identity,
            }

    adsorption = {}
    for state in ("new_state", "state701"):
        values = {}
        for gas in ("xe", "kr"):
            energy = complexes[state][gas]["energy_eV"]
            values[f"E_{gas}_complex_eV"] = energy
            values[f"E_ads_{gas}_eV"] = energy - bare[state]["energy_eV"] - gas_energies[gas]
        values["Xe_minus_Kr_adsorption_eV"] = values["E_ads_xe_eV"] - values["E_ads_kr_eV"]
        adsorption[state] = values

    selectivity_shift_meV = 1000.0 * (
        adsorption["new_state"]["Xe_minus_Kr_adsorption_eV"]
        - adsorption["state701"]["Xe_minus_Kr_adsorption_eV"]
    )
    if not bare_complete:
        reasons.append("bare supercell did not pass electronic/OMC completion checks")
    if bare_separation["joint_down_frobenius"] < 0.5:
        reasons.append("bare new/701 signatures collapsed in the 1x1x2 supercell")
    if not all(item["pass"] for item in identity.values()):
        reasons.append("at least one Xe/Kr state failed matrix identity or SCF checks")
        decision = "STOP_STATE_PRESERVATION_GATE"
    elif abs(selectivity_shift_meV) < 6.0:
        reasons.append("state-dependent Xe/Kr shift is below the 6 meV upper resolution edge")
        decision = "STOP_BELOW_RESOLUTION"
    elif abs(selectivity_shift_meV) < 12.0:
        reasons.append(
            "state-dependent Xe/Kr shift is outside 6 meV but below the 12 meV clear-signal threshold"
        )
        decision = "BORDERLINE_REPEAT_ONLY"
    else:
        decision = "PASS_TO_REPLICATION_AND_HIGHER_SETTINGS"

    payload = {
        "phase": "gas",
        "decision": decision,
        "reasons": reasons,
        "bare_state_separation": bare_separation,
        "gas_reference_energies_eV": gas_energies,
        "state_identity": identity,
        "adsorption": adsorption,
        "state_dependent_selectivity_shift_meV": selectivity_shift_meV,
        "hard_gate": {
            "stop_below_meV": 6.0,
            "borderline_meV": [6.0, 12.0],
            "advance_at_or_above_meV": 12.0,
        },
        "cases": {
            state: {gas: json_safe_case(case) for gas, case in cases.items()}
            for state, cases in complexes.items()
        },
    }
    write_report(root, "gas", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return (
        0
        if decision == "PASS_TO_REPLICATION_AND_HIGHER_SETTINGS"
        else {
            "STOP_STATE_PRESERVATION_GATE": 2,
            "STOP_BELOW_RESOLUTION": 3,
            "BORDERLINE_REPEAT_ONLY": 4,
        }[decision]
    )


if __name__ == "__main__":
    raise SystemExit(main())
