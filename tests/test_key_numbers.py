from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_key_numbers() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/verify_key_numbers.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    claims = report["merged_jctc_claims"]
    co3 = report["co3_second_framework"]

    assert claims["occupation_state_selectivity_order"]["control"] == ["Pd", "Ni", "Pt"]
    assert claims["occupation_state_selectivity_order"]["Mx"] == ["Ni", "Pd", "Pt"]
    assert claims["Pd_Pt_anchored_control_selectivity_shift_range_meV"] == [
        8.83451,
        9.08136,
    ]
    assert claims["Pd_Pt_same_protocol_control_selectivity_shift_range_meV"] == [
        14.1462,
        14.20766,
    ]
    assert claims["six_hundred_eV_Ni_Pt_Kr_gap_meV"] == 1.27066
    assert co3["new_minus_ref701_333_600_meV"] == -6.0948
    assert co3["new_minus_ref701_444_650_meV"] == -6.17729
    assert co3["control_high_setting_identity_preserved"] is False
