# Co3-squarate target-specific reproduction

Status date: 2026-10-24

## Completed source reproduction

The resumed queue at `remote:/jctc_co_squarate_repro_20261023` completed
at `2026-10-23T17:37:03Z` after about 22 minutes of VASP work.

Both cases contain `RUN_COMPLETE`; the root contains `REPRO_COMPLETE`.
Every stage2 output passed the project checks for:

- `OCCEXT=0`;
- `EDIFF=1E-6` reached;
- no `NELM` abort;
- the audited `ENCUT=600`, PBE, DFT+U, and magnetic settings.

### Case 1: repro_co3_701_default

| Quantity | Original co3_seed701 | Default reproduction |
|---|---:|---:|
| Final energy / eV | -161.41473210 | -161.41473664 |
| Total magnetic moment / uB | 9.0 | 9.0 |
| Site d moments / uB | 2.8033, 2.8033, 2.8012 | 2.8034, 2.8034, 2.8012 |

The reproduced energy differs from the original by -0.00454 meV.
The three-Co joint occupation-matrix distances to the original state are:

- spin-up: `0.00017321`;
- spin-down: `0.00110000`.

This is a strong numerical reproduction of the original `co3_seed701` state.

### Case 2: repro_co3_702_algoall

This run did not return to the original `co3_seed702` branch. After target
matrix constraint and `ALGO=All` release, it converged to a lower state:

| Quantity | Original co3_seed702 | ALGO=All reproduction |
|---|---:|---:|
| Final energy / eV | -161.41448722 | -161.42541039 |
| Total magnetic moment / uB | 9.0 | 9.0 |
| Site d moments / uB | 2.8031, 2.8032, 2.8019 | 2.8035, 2.8034, 2.8004 |

The new state is about `10.92 meV` below the original `co3_seed702` and about
`10.67 meV` below the reproduced `701` state.

The three-Co joint occupation-matrix distance to the original `702` is:

- spin-up: `0.00328024`;
- spin-down: `0.62566819`.

The distance from the reproduced `701` state is:

- spin-up: `0.00494874`;
- spin-down: `1.29656303`.

Therefore the original near-degenerate 701/702 pair was not reproduced by the
`ALGO=All` release path. The calculation found a distinct, lower candidate
state while preserving the total 9 uB moment.

## Completed minimal reproduction

The exact-input duplicate completed at
`2026-10-23T17:59:18Z` in about 21 minutes 36 seconds:

`remote:/jctc_co_squarate_repro_dup1_20261024`

The POSCAR, POTCAR, KPOINTS, INCAR, and OCCMATRIX SHA256 values are identical
to the first `repro_co3_702_algoall` run. The duplicate contains
`RUN_COMPLETE` and passes the independent stage1 and stage2 checks for
`OCCEXT`, EDIFF, NELM, POTCAR ordering, ENCUT, DFT+U, and magnetic settings.

| Quantity | New state A | Independent duplicate B |
|---|---:|---:|
| Final energy / eV | -161.4254103900 | -161.4254103900 |
| Total magnetic moment / uB | 9.0 | 9.0 |
| Site d moments / uB | 2.8035, 2.8034, 2.8004 | 2.8035, 2.8034, 2.8004 |

For all three Co atoms, both the spin-up and spin-down matrix Frobenius
distances between A and B are `0.0000000000`. The joint up/down distances are
also `0.0000000000`.

The new state is therefore reproducible under the tested target-matrix and
`ALGO=All` path. It is distinct from the original `702` state:

- energy: about `10.923 meV` lower than original `702`;
- joint spin-up matrix distance: `0.0032802439`;
- joint spin-down matrix distance: `0.6256681948`.

The defensible conclusion is:

1. `co3_seed701` is numerically reproduced by the default solver.
2. The original `co3_seed702` is not reproduced by the `ALGO=All` release.
3. `ALGO=All` instead finds a lower, independently reproducible SCF state.
4. The original 701/702 near-degenerate pair cannot yet be described as two
   equally reproducible stationary branches. The original 702 remains a valid
   observed output, but its solver-path robustness is now disfavored.
5. No matrix expansion is justified from this result alone.

## Solver-path gate

Two additional target-702 controls kept every physical input fixed and changed
only the electronic minimizer:

- VASP default (IALGO=38) did not reach EDIFF and was safety-stopped at
  iteration 64 with `rms(c)` still about `1.21e-2`;
- `ALGO=Fast` did not reach EDIFF and was stopped at iteration 61 with
  `rms(c)` about `5.43e-2`;
- neither partial output is a valid final state.

The matrix-spectrum comparison is more informative than the raw Frobenius
distance. New state versus original 702 has a Co-3 spin-down matrix distance of
`0.62554`, but its five eigenvalues differ by at most `0.00297`. The difference
is therefore dominated by an orientation/off-diagonal rotation in the fixed d
basis, not a simple high-spin to low-spin population transfer.

Detailed solver gate:

`source:/co_squarate_repro_20261024\SOLVER_GATE.md`

The interrupted partial from the VM crash is preserved under:

`repro_20261023/interrupted/repro_co3_702_algoall_stage1_20261023T171454Z`

It is evidence only and was not used as a final result.

## Local preserved outputs

- Completed source reproduction:
  `source:/co_squarate_repro_20261024`
- Independent duplicate:
  `source:/co_squarate_repro_dup1_20261024`
