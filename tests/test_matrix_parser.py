from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_occupation_matrix import parse_outcar  # noqa: E402


def test_complete_co3_matrix_is_read() -> None:
    outcar = ROOT / "data" / "raw_text_outputs" / "co3" / "selected" / "new_444_650" / "OUTCAR"
    up, down = parse_outcar(outcar, atom=1)
    assert len(up) == len(down) == 5
    assert all(len(row) == 5 for row in up + down)
