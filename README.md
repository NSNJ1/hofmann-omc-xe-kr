# State-aware DFT+U calculations for Xe/Kr separation in Hofmann frameworks

This repository contains the numerical source data, analysis code, selected
VASP input/output files, and figure-generation scripts associated with a study
of self-consistent Co 3d occupation-matrix states in
Co(pyz)[M(CN)4] (M = Ni, Pd, Pt) and a second Co-O framework.

The central point is not that one SCF endpoint is "the" energy of a material.
It is that a converged calculation selects one electronic solution, and the
same state-aware treatment must be applied to both the guest-loaded and
guest-free cells before a meV-scale adsorption comparison is interpreted.

## What is included

- Processed numerical tables used by the manuscript and the main plotting
  scripts.
- Independent checks of the load-bearing numbers reported in the paper.
- Occupation-matrix parsing and comparison tools.
- Representative VASP text inputs and outputs for the second-framework
  calculations.
- Representative Hofmann `INCAR`, `KPOINTS`, `POSCAR`, and `CONTCAR` files.
- Reports describing successful and failed/stalled solver paths.
- Reduced charge-density slices and their summary table.
- Publication-quality SVGs and PDFs regenerated from the released source
  data.

## What is intentionally not included

- `POTCAR` files, VASP binaries, and the OMC-enabled VASP binary. VASP and its
  PAW datasets must be obtained under the user's own license.
- `WAVECAR` files and the full 3D `CHGCAR` volume files. The reduced 120 x 120
  charge-density slices and their integral table are provided instead.
- Third-party papers, templates, or licensed software.

The full historical workspace from the superseded v1.0.0 release is retained
locally at `E:\git\hofmann-omc-xe-kr-full-v1.0.0`. The public repository is
the curated v1.1.0 release.

## Quick start

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python scripts/verify_key_numbers.py --output verification_key_numbers.json
python scripts/make_v20_data_figures.py
python scripts/make_co3_figures.py
python -m pytest
python scripts/check_release.py
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1`.

## Reproduce the released figures

The two plotting entry points write to `figures/rebuilt/`:

```bash
python scripts/make_v20_data_figures.py
python scripts/make_co3_figures.py
```

The scripts read only files inside this repository. They do not call VASP and
do not require access to the original calculation cluster.

## Verify the numerical claims

```bash
python scripts/verify_key_numbers.py --output verification_key_numbers.json
```

This recomputes the state-dependent selectivity shifts, the complex/bare
energy cancellation, the 650 eV energy checks, and the selected
Co3-squarate state separations from the released tables.

## Repository layout

| Path | Contents |
|---|---|
| `data/source_tables/hofmann_closeout/` | Final Hofmann energy, state, convergence, and selectivity tables |
| `data/source_tables/hofmann_figure_20261025/` | Machine-readable source table for the target-family figure |
| `data/source_tables/v20_workdata/` | Figure-ready chemical-control, resolution, and cell-response tables |
| `data/source_tables/v20_origin/` | Long-form plotting exports for the v20 figure set |
| `data/source_tables/co3/` | Co3-squarate matrices, state distances, DOS, and gate reports |
| `data/raw_text_outputs/co3/` | Selected VASP text outputs for the Co3-squarate calculations |
| `data/inputs/hofmann_archive/` | Archived Hofmann VASP input and relaxed-structure text files |
| `data/charge_density/` | Reduced differential-density slices and integral summary |
| `scripts/` | Parsers, numerical verification, plotting, and release checks |
| `docs/` | Data dictionary, numerical scope, provenance, and VASP notes |
| `tests/` | Regression tests for the released numbers and parsers |

## Scientific scope

The adsorption ranking result is limited to the tested Hofmann family. The
Pd/Pt response is reported as a Ni-Kr target-family response, not as exact
cross-metal identity of complete 5 x 5 matrices. The second Co-O framework
tests state existence and protocol sensitivity; its single-site adsorption
pilot does not establish a second material ranking.

See [docs/METHOD_SCOPE.md](docs/METHOD_SCOPE.md) for the exact claim
boundaries and [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) for field
definitions.

## Software and calculation settings

The released data were generated with VASP 6.4.3 using PBE, PAW potentials,
the Dudarev DFT+U formulation, and zero-damping DFT-D3. The Hofmann
calculations used a 600 eV cutoff and a Gamma-centered 4 x 4 x 4 mesh. The
Co3-squarate checks used Co `Ueff = 6.4 eV`, 3 x 3 x 3 and 4 x 4 x 4 meshes,
and 600/650 eV cutoffs. Full settings are listed in
[docs/VASP_AND_REPRODUCIBILITY.md](docs/VASP_AND_REPRODUCIBILITY.md).

## Licenses and citation

Original code in this repository is released under the MIT License. Original
data tables, structures, and reduced density data are released under CC BY
4.0, subject to the upstream rights of the published parent structures. See
[LICENSE](LICENSE) and [DATA_LICENSE.md](DATA_LICENSE.md).

Citation metadata is provided in `CITATION.cff`. The archived release and its
DOI will be listed there and in the manuscript's Data and Code Availability
statement.

## Contact

Open an issue in this repository for questions about the data layout or
reproduction scripts. Questions requiring VASP/OMC implementation details
should identify the relevant calculation folder in
`data/raw_text_outputs/co3/`.
