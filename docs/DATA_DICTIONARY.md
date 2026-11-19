# Data dictionary

All files are UTF-8 text unless noted otherwise.

## Hofmann closeout tables

Directory: `data/source_tables/hofmann_closeout/`

| File | Purpose |
|---|---|
| `standard_eads_branches.csv` | Paired complex/bare energies, branch labels, matrix distances, and adsorption energies |
| `standard_selectivity.csv` | Xe and Kr adsorption energies and `S = Eads(Xe) - Eads(Kr)` for each metal and electronic branch |
| `standard_complex_states.csv` | State shifts and full-matrix distances for gas-loaded cells |
| `standard_bare_states.csv` | State shifts and full-matrix distances for guest-free cells |
| `standard_control_residuals.csv` | Difference between archived and recomputed control energies |
| `standard_ranking.csv` | Metal ranking for each electronic branch |
| `convergence_results.csv` | Numerical convergence and branch-assignment checks |
| `extended_random_raw.csv` | Individual random-start results before summarization |
| `extended_random_summary.csv` | Aggregated random-start results |
| `highcut_*` | 650 eV checks for the target-family calculations |

Important units:

- total energies and adsorption energies are in `eV` unless a column ends in
  `meV`;
- matrix distances are dimensionless Frobenius distances;
- diagonal L1 values are not complete-matrix distances.

`eads_meV` and `same_protocol_eads_meV` represent two control definitions. Do
not treat them as duplicate measurements of one quantity. The manuscript
reports the resulting ranges rather than a single universal shift.

## Target-family figure data

File: `data/source_tables/hofmann_figure_20261025/fig2_target_family_source.csv`

The long-form columns are:

| Column | Meaning |
|---|---|
| `panel` | Figure panel identifier |
| `metal` | Ni, Pd, or Pt |
| `gas` | Xe or Kr |
| `metric` | `complex_shift`, `bare_shift`, or `family_matched_eads_shift` |
| `value_meV` | Energy change relative to the assigned control |

Negative values are lower total or adsorption energies. For selectivity,
`S = Eads(Xe) - Eads(Kr)`, so more negative `S` means stronger Xe preference.

## v20 plotting tables

Directories:

- `data/source_tables/v20_workdata/`
- `data/source_tables/v20_origin/`

These are the machine-readable exports used by the released plotting script.
They include metal/ligand control energies, selectivity changes, volume and
cell-shape response, cutoff and k-point checks, methyl contact/relaxation
terms, and guest-sphere reduced-density integrals.

The `v20_origin` directory contains long-form data prepared for plotting. The
`professional_figures_20261026/workdata_v3` source names were normalized to
`v20_workdata` in this release.

## Co3-squarate tables and reports

Directory: `data/source_tables/co3/`

| File | Purpose |
|---|---|
| `co3_high_setting_matrices.csv` | Complete 5 x 5 spin-up/down matrices for the two selected Co3-squarate solutions |
| `co3_matrix_distance_summary.csv` | Per-Co and joint Frobenius distances |
| `co3_spin_resolved_dos_long.csv` | Long-form total spin-resolved DOS |
| `CONTROL_LOW_POSTRELAX_GATE.json` | Machine-readable control-transfer gate |
| `GAS_ANALYSIS.json` | Numerical output of the common-site Xe/Kr pilot |
| `PHASE0_ANALYSIS.json` | Bare-supercell state-preservation gate |
| `PILOT_RESULT_20261026.md` | Human-readable interpretation and decision |
| `SOLVER_GATE.md` | Failed/path-dependent solver checks |

The Co3-squarate results are a second-framework state test. They are not a
second quantitative adsorption ranking.

## Charge-density data

Directory: `data/charge_density/`

| File | Meaning |
|---|---|
| `summary.csv` | Signed and absolute reduced-density integrals, including sphere radii |
| `slice_*.csv` | 120 x 120 slices of the reduced density in `e/Angstrom^3` |
| `README.md` | Original derivation notes |

`summary.csv` contains three quantities that must not be conflated:

1. Bader populations;
2. sphere-integrated differential density;
3. full-cell integrated absolute differential density.

The released slices are derived from licensed VASP density volumes. The full
`CHGCAR` volumes are not redistributed.

## Raw Co3 VASP text files

Directory: `data/raw_text_outputs/co3/selected/`

Six normalized calculation folders are retained:

- `new_333_600`, `ref701_333_600`, and `control_333_600`;
- `new_444_650`, `ref701_444_650`, and `control_444_650`.

Each contains the final `INCAR`, `KPOINTS`, `POSCAR`, `CONTCAR`, and `OUTCAR`.
The complete historical workspace remains in the local full archive, while
the selected outputs here are sufficient to verify the published state
separations and the failed high-setting control identity.

## Hofmann input archive

Directory: `data/inputs/hofmann_archive/`

This tree contains three representative archived calculation folders:
Pd-H-Xe (`02_Xe_v4`), Pt-H-Xe (`12_Pt_Xe`), and Ni-H-Kr (`16_Ni_Kr`).
Each includes `INCAR`, `KPOINTS`, `POSCAR`, and `CONTCAR`. `POTCAR` is
omitted. The complete input archive remains in the local v1.0.0 snapshot.
