# VASP settings and reproducibility

## Core settings

The calculations used VASP 6.4.3, the PBE functional, PAW potentials, the
Dudarev DFT+U formulation, collinear spin polarization, and zero-damping
DFT-D3.

Hofmann family:

- Co `Ueff = 3.5 eV`;
- plane-wave cutoff `ENCUT = 600 eV`;
- Gamma-centered `4 x 4 x 4` Monkhorst-Pack mesh;
- Gaussian smearing `0.05 eV`;
- SCF `EDIFF = 1e-6 eV`;
- fixed-cell ionic relaxation to `0.02 eV/Angstrom`.

Co3-squarate:

- Co `Ueff = 6.4 eV`;
- `3 x 3 x 3` mesh at 600 eV and `4 x 4 x 4` at 650 eV;
- fixed-cell, hydrogen-only, and all-ion geometry gates are labelled
  separately;
- the control-transfer and solver-path failures are retained as negative
  evidence.

## Occupation-matrix workflow

Static calculations used `LDAUPRINT = 2`. The stage-1 input applies a target
`OCCMATRIX`. Stage 2 sets `OCCEXT = 0` to release that constraint. Only the
released endpoint is eligible for an energy comparison.

The parser in `scripts/extract_occupation_matrix.py` reads the final collinear
occupation matrix from `OUTCAR`. The comparison code symmetrizes numerical
asymmetry before computing Frobenius distances and eigenvalues.

## What is reproducible from this repository

- parsing and comparing released `OCCMATRIX`/`OUTCAR` data;
- recomputing the key energy and selectivity values;
- regenerating source-data figures;
- checking successful and failed solver paths;
- rebuilding all tables from the delivered textual outputs.

The original Fourier-transform workflow and full VASP execution are not
rerun by the default test suite. They require a licensed VASP installation,
matching PAW datasets, and an OMC-enabled binary.

## Why `POTCAR`, `WAVECAR`, and full `CHGCAR` files are absent

`POTCAR` datasets and the VASP executable are licensed software and are not
redistributed. `WAVECAR` and full `CHGCAR` files are large volumetric outputs;
the repository contains the reduced density slices and summaries needed for
the published charge-density panel instead.
