# Target-702 solver-path gate

Date: 2026-10-24

## Purpose

The original `co3_seed702` and `co3_seed701` were separated by only
`0.24488 meV`, but their three-Co matrices differed strongly. A prior
`ALGO=All` release from the complete `co3_seed702` matrix converged twice to a
new state at `-161.4254103900 eV`, not to the original `702` state.

This gate isolates the solver variable while keeping the 702 target matrix,
geometry, ENCUT, k mesh, DFT+U, magnetization, and smearing fixed.

## Results

| Route | Stage 1 | Stage 2 outcome |
|---|---|---|
| VASP default (IALGO=38) | converged in 26 DAV, E0=-161.41716 eV | no EDIFF convergence; safety-stopped at DAV 64 |
| `ALGO=Fast` | converged in 28 RMM, E0=-161.41717 eV | no EDIFF convergence; safety-stopped at RMM 61 |
| `ALGO=All` run A | converged | converged to -161.4254103900 eV |
| `ALGO=All` run B | converged | identical energy and identical matrices |

The default path reached `rms(c) = 1.21e-2` at iteration 64 after repeated
rises and falls. Fast reached `rms(c) = 5.43e-2` at iteration 61. Neither was
approaching `EDIFF=1e-6`. Both partial outputs were preserved under each
queue's `interrupted/` directory and are explicitly excluded from final
energies or matrices.

## Occupation-matrix spectrum

The reproducible lower state and the original 702 state have nearly identical
local d-shell eigenvalues. The largest per-matrix eigenvalue change is
`0.00297`, while the Co-3 spin-down matrix Frobenius distance is `0.62554`.

Key comparison, new state versus original 702:

| Site/spin | max eigenvalue difference | matrix Frobenius difference |
|---|---:|---:|
| Co1 up | 0.000176 | 0.000316 |
| Co1 down | 0.000307 | 0.008860 |
| Co2 up | 0.000176 | 0.000316 |
| Co2 down | 0.000404 | 0.009000 |
| Co3 up | 0.001628 | 0.003250 |
| Co3 down | 0.002970 | 0.625541 |

All states keep a total moment of 9 uB and local d moments near 2.80 uB.
Therefore the difference is not a simple high-spin/low-spin population change.
It is dominated by a rotation of the Co-3 spin-down occupation matrix relative
to the fixed VASP d basis.

## Scientific consequence

The original 701/702 pair cannot currently be called two equally robust,
near-degenerate stationary branches. The original 702 value remains a valid
recorded output of its original trajectory, but target-matrix reinsertion does
not recover it under default or Fast minimization. Under the only tested
route that converges, it falls to a lower matrix-rotated state.

No additional solver variants will be added. The next meaningful gate is
k-point sensitivity at fixed geometry, beginning with a denser mesh for the
reproducible lower state.
